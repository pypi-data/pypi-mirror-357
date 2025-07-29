import copy
import fire
import time
import pandas as pd
import matplotlib.pyplot as plt
import pytagi.metric as metric
from pytagi import Normalizer as normalizer
from canari import (
    DataProcess,
    Model,
    ModelOptimizer,
    SKF,
    SKFOptimizer,
    plot_data,
    plot_prediction,
    plot_skf_states,
    plot_states,
)
from canari.component import LocalTrend, LocalAcceleration, LstmNetwork, WhiteNoise

# Fix parameters
sigma_v_fix = 0.07835596785011355
look_back_len_fix = 12
SKF_std_transition_error_fix = 2.9874712252910025e-04
SKF_norm_to_abnorm_prob_fix = 3.2834494053648664e-05


def main(
    num_trial_optimization: int = 20,
    param_optimization: bool = False,
    param_grid_search: bool = False,
):
    # Read data
    data_file = "./data/benchmark_data/test_13_monthly_data.csv"
    df_raw = pd.read_csv(data_file, skiprows=1, delimiter=",", header=None)
    time_series = pd.to_datetime(df_raw.iloc[:, 0])
    df_raw = df_raw.iloc[:, 1:]
    df_raw.index = time_series
    df_raw.index.name = "date_time"
    # Data pre-processing
    output_col = [0]
    data_processor = DataProcess(
        data=df_raw,
        time_covariates=["month_of_year"],
        train_split=0.2,
        validation_split=2.5e-02,
        output_col=output_col,
    )
    train_data, validation_data, test_data, all_data = data_processor.get_splits()

    # Define model
    def initialize_model(param, train_data, validation_data):
        model = Model(
            LocalTrend(),
            LstmNetwork(
                look_back_len=param["look_back_len"],
                num_features=2,
                num_layer=1,
                num_hidden_unit=50,
                device="cpu",
                manual_seed=1,
            ),
            WhiteNoise(std_error=param["sigma_v"]),
        )
        # index_start = 0
        # index_end = 12 * 3
        # y1 = data_processor.train_data["y"][index_start:index_end].flatten()
        # trend, _, seasonality, _ = DataProcess.decompose_data(y1)
        # t_plot = data_processor.data.index[index_start:index_end].to_numpy()
        # plt.plot(t_plot, trend, color="b")
        # plt.plot(t_plot, seasonality, color="orange")
        # plt.scatter(t_plot, y1, color="k")
        # plt.plot(
        #     data_processor.get_time("train"),
        #     data_processor.get_data("train", standardization=True),
        #     color="r",
        # )
        # plt.show()

        model.auto_initialize_baseline_states(train_data["y"][0 : 12 * 3])
        states_optim = None
        mu_validation_preds_optim = None
        std_validation_preds_optim = None
        num_epoch = 100
        for epoch in range(num_epoch):
            mu_validation_preds, std_validation_preds, states = model.lstm_train(
                train_data=train_data,
                validation_data=validation_data,
            )
            model.set_memory(states=states, time_step=0)

            mu_validation_preds_unnorm = normalizer.unstandardize(
                mu_validation_preds,
                data_processor.scale_const_mean[data_processor.output_col],
                data_processor.scale_const_std[data_processor.output_col],
            )

            std_validation_preds_unnorm = normalizer.unstandardize_std(
                std_validation_preds,
                data_processor.scale_const_std[data_processor.output_col],
            )

            validation_obs = data_processor.get_data("validation").flatten()
            validation_log_lik = metric.log_likelihood(
                prediction=mu_validation_preds_unnorm,
                observation=validation_obs,
                std=std_validation_preds_unnorm,
            )

            model.early_stopping(
                evaluate_metric=-validation_log_lik,
                current_epoch=epoch,
                max_epoch=num_epoch,
            )
            model.metric_optim = model.early_stop_metric

            if epoch == model.optimal_epoch:
                mu_validation_preds_optim = mu_validation_preds.copy()
                std_validation_preds_optim = std_validation_preds.copy()
                states_optim = copy.copy(states)

            if model.stop_training:
                break

        return (
            model,
            states_optim,
            mu_validation_preds_optim,
            std_validation_preds_optim,
        )

    # Define parameter search space
    if param_optimization or param_grid_search:
        if param_optimization:
            param_space = {
                "look_back_len": [6, 15],
                "sigma_v": [1e-3, 2e-1],
            }
        elif param_grid_search:
            param_space = {
                "look_back_len": [6, 15],
                "sigma_v": [1e-3, 2e-1],
            }
        # Define optimizer
        model_optimizer = ModelOptimizer(
            model=initialize_model,
            param_space=param_space,
            train_data=train_data,
            validation_data=validation_data,
            num_optimization_trial=num_trial_optimization,
            grid_search=param_grid_search,
        )
        model_optimizer.optimize()
        # Get best model
        param = model_optimizer.get_best_param()
    else:
        param = {
            "look_back_len": look_back_len_fix,
            "sigma_v": sigma_v_fix,
        }

    # Train best model
    print("Model parameters used:", param)
    model_optim, states_optim, mu_validation_preds, std_validation_preds = (
        initialize_model(param, train_data, validation_data)
    )

    # Save best model for SKF analysis later
    model_optim_dict = model_optim.get_dict()

    # Plot
    fig, ax = plt.subplots(figsize=(10, 6))
    plot_data(
        data_processor=data_processor,
        standardization=True,
        plot_test_data=False,
        plot_column=output_col,
        validation_label="y",
        plot_nan=False,
    )
    plot_prediction(
        data_processor=data_processor,
        mean_validation_pred=mu_validation_preds,
        std_validation_pred=std_validation_preds,
        validation_label=[r"$\mu$", f"$\pm\sigma$"],
    )
    plot_states(
        data_processor=data_processor,
        states=states_optim,
        standardization=True,
        states_to_plot=["level"],
        sub_plot=ax,
    )
    plt.legend()
    plt.title("Validation predictions")
    plt.show()

    # Define SKF model
    def initialize_skf(skf_param, model_param: dict):
        norm_model = Model.load_dict(model_param)
        abnorm_model = Model(
            LocalAcceleration(),
            LstmNetwork(),
            WhiteNoise(),
        )
        skf = SKF(
            norm_model=norm_model,
            abnorm_model=abnorm_model,
            std_transition_error=skf_param["std_transition_error"],
            norm_to_abnorm_prob=skf_param["norm_to_abnorm_prob"],
        )
        skf.save_initial_states()
        return skf

    # Define parameter search space
    slope_upper_bound = 2e-1
    slope_lower_bound = 1e-3

    # # Plot synthetic anomaly
    synthetic_anomaly_data = DataProcess.add_synthetic_anomaly(
        train_data,
        num_samples=1,
        slope=[slope_lower_bound, slope_upper_bound],
    )
    plot_data(
        data_processor=data_processor,
        standardization=True,
        plot_validation_data=False,
        plot_test_data=False,
        plot_column=output_col,
        train_label="data without anomaly",
        plot_nan=False,
    )

    train_time = data_processor.get_time("train")
    for ts in synthetic_anomaly_data:
        plt.plot(train_time, ts["y"])
    plt.legend(
        [
            "data without anomaly",
            "",
            "smallest anomaly tested",
            "largest anomaly tested",
        ]
    )
    plt.title("Train data with added synthetic anomalies")
    plt.show()

    if param_grid_search or param_optimization:
        if param_grid_search:
            skf_param_space = {
                "std_transition_error": [1e-6, 1e-5, 1e-4, 1e-3],
                "norm_to_abnorm_prob": [1e-6, 1e-5, 1e-4, 1e-3],
                "slope": [0.002, 0.004, 0.006, 0.008, 0.01, 0.03, 0.05, 0.07, 0.09],
            }
        elif param_optimization:
            skf_param_space = {
                "std_transition_error": [1e-6, 1e-3],
                "norm_to_abnorm_prob": [1e-6, 1e-3],
                "slope": [slope_lower_bound, slope_upper_bound],
            }
        skf_optimizer = SKFOptimizer(
            initialize_skf=initialize_skf,
            model_param=model_optim_dict,
            param_space=skf_param_space,
            data=train_data,
            num_synthetic_anomaly=50,
            num_optimization_trial=num_trial_optimization * 2,
            grid_search=param_grid_search,
        )
        skf_optimizer.optimize()
        # Get parameters
        skf_param = skf_optimizer.get_best_param()
    else:
        skf_param = {
            "std_transition_error": SKF_std_transition_error_fix,
            "norm_to_abnorm_prob": SKF_norm_to_abnorm_prob_fix,
        }

    print("SKF model parameters used:", skf_param)
    skf_optim = initialize_skf(skf_param, model_optim_dict)

    # Detect anomaly
    filter_marginal_abnorm_prob, states = skf_optim.filter(data=all_data)
    smooth_marginal_abnorm_prob, states = skf_optim.smoother(matrix_inversion_tol=1e-2)

    fig, ax = plot_skf_states(
        data_processor=data_processor,
        states=states,
        # states_to_plot=["level", "trend", "lstm", "white noise"],
        states_type="smooth",
        model_prob=filter_marginal_abnorm_prob,
        standardization=False,
        color="b",
        plot_nan=False,
    )
    fig.suptitle("SKF hidden states", fontsize=10, y=1)
    plt.show()

    if param_optimization or param_grid_search:
        print("Model parameters used:", model_optimizer.param_optim)
        print("SKF model parameters used:", skf_optimizer.param_optim)
        print("-----")
    else:
        print("Model parameters used:", param)
        print("SKF model parameters used:", skf_param)
        print("-----")


if __name__ == "__main__":
    start_time = time.time()
    fire.Fire(main)
    end_time = time.time()
    print(f"Run time: {end_time-start_time:.2f} seconds")
