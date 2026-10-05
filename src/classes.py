import pandas as pd
import matplotlib.pyplot as plt

class BioprocessMonitor:
    def __init__(self, filepath: str, ph_lims: tuple, temperature_lims: tuple):
        self.filepath = filepath
        self.ph_min = ph_lims[0]
        self.ph_max = ph_lims[1]
        self.temperature_min = temperature_lims[0]
        self.temperature_max = temperature_lims[1]
        self.df = pd.read_csv(self.filepath)

    def extract_batch(self, batch_id: int):

        return self.df[self.df["batch_id"] == batch_id]

    def optimal_ph_mask(self, df_batch: pd.DataFrame):
# Finds the pH batches which falls between the upper and lower limits
        return (df_batch["pH"] >= self.ph_min) & (df_batch["pH"] <= self.ph_max)

    def optimal_temperature_mask(self, df_batch: pd.DataFrame):
# Finds the temperature batches which falls between the upper and lower limits and returns the result
        return (df_batch["temperature_C"] >= self.temperature_min) & (df_batch["temperature_C"] <= self.temperature_max)

    def get_n_batches(self):
# Finds the number of distinct batches
        return self.df["batch_id"].nunique()

    def export_dashboard(self, batch_id: int, filepath: str):

# Creates the figure canvas with the specified dimensions
        df_batch = self.extract_batch(batch_id)
        fig, ax = plt.subplots(2, 2, figsize=(10, 8), dpi=200, layout="constrained")

# Top-Left Scatter Plot
        ax[0, 0].scatter(df_batch["time_h"], df_batch["C_glucose_g_L^-1"], label="Glucose", marker = "o")
        ax[0, 0].scatter(df_batch["time_h"], df_batch["C_biomass_g_L^-1"], label="Biomass", marker = "*")
        ax[0, 0].scatter(df_batch["time_h"], df_batch["C_product_g_L^-1"], label="Product", marker = "+")
        ax[0, 0].set_xlabel("Time [h]")
        ax[0, 0].set_ylabel("Concentration [g/L]")
        ax[0, 0].legend()
# Top-Right Scatter Plot
        temp_mask = self.optimal_temperature_mask(df_batch)
        ax[0, 1].scatter(df_batch.loc[temp_mask, "time_h"], df_batch.loc[temp_mask, "temperature_C"], color = "green", marker = "o", label="Optimal")
        ax[0, 1].scatter(df_batch.loc[~temp_mask, "time_h"], df_batch.loc[~temp_mask, "temperature_C"], color = "red", marker = "x", label="Sub-Optimal")
        ax[0, 1].set_xlabel("Time [h]")
        ax[0, 1].set_ylabel("Temperature [°C]")
        ax[0, 1].legend()
# Bottom-Left Scatter Plot
        ph_mask = self.optimal_ph_mask(df_batch)
        ax[1, 0].scatter(df_batch.loc[ph_mask, "time_h"], df_batch.loc[ph_mask, "pH"], color = "green", marker = "o", label="Optimal")
        ax[1, 0].scatter(df_batch.loc[~ph_mask, "time_h"], df_batch.loc[~ph_mask, "pH"], color = "red", marker = "x", label="Sub-Optimal")
        ax[1, 0].set_xlabel("Time [h]")
        ax[1, 0].set_ylabel("pH")
        ax[1, 0].legend()
# Bottom-Right Scatter Plot
        ax[1, 1].scatter(df_batch["time_h"], df_batch["DO_percent"])
        ax[1, 1].set_xlabel("Time [h]")
        ax[1, 1].set_ylabel("Dissolved Oxygen (DO) [%]")

        for axes in ax.flat:
            axes.tick_params(axis="both", which="major", labelsize=10)
            axes.set_xticks(range(0, 49, 6))
# To save the figure to the file path
        fig.savefig(filepath)
# Close the figure to free up memory
        plt.close(fig)

    def export_summary(self, filepath: str):

        df_summary = pd.DataFrame()
        for batch_id in range(1, self.get_n_batches() + 1):

            df_batch = self.extract_batch(batch_id)

            ph_mask = self.optimal_ph_mask(df_batch)
            temp_mask = self.optimal_temperature_mask(df_batch)
# Calculates the percent and rounds the number to 2 decimals
            ph_optimal_percent = round(ph_mask.mean() * 100, 2)
            temp_optimal_percent = round(temp_mask.mean() * 100, 2)
            final_product = df_batch["C_product_g_L^-1"].iloc[-1]

            df_summary.loc[batch_id - 1, "batch_id"] = batch_id
            df_summary.loc[batch_id -1, "pH_optimal_percent"] = ph_optimal_percent
            df_summary.loc[batch_id -1, "temperature_optimal_percent"] = temp_optimal_percent
            df_summary.loc[batch_id -1, 'C_product_g_L^-1'] = final_product

# Creates a list of the columns to be exported:
        columns_export = ["batch_id", "pH_optimal_percent", "temperature_optimal_percent", "C_product_g_L^-1"]
        df_export = df_summary.loc[:, columns_export]
        df_export.to_csv(filepath, index=False)
