from fileinput import filename
import matplotlib.pyplot as plt 
import pandas as pd
import numpy as np
from pathlib import Path


class AktaVisualiser:
    def __init__(self, file_path):
        self.file_path = file_path
        self.data = None

    def read_data(_heparinself):
        """Reads the AKTA data from the CSV file."""
        self.data = pd.read_csv(
            self.file_path,
            encoding='utf-16',
            sep='\t',
            skiprows=3, #Removes unneccesary metadata
            usecols=[0, 1, 2, 3, 4, 5, 12, 13], #Removes unneccesary columns contaitng metadata
            header=None, #Used to give a broader use
            names=[ 
                "ConcB[mL]", "ConcB[%]", "Conductivity[mL]",
                "Conductivity[mS/cm]", "UV[mL]", "UV[mAU]",
                "Fraction[mL]", "Fraction[n]"])
        return self.data

    def read_data_affinity(self):
        """Reads the AKTA data from the CSV file.
        Specifically handles affinity chromatography measured at A280, since the relevant rows are selected"""
        self.data = pd.read_csv(
            self.file_path,
            encoding='utf-16',
            sep='\t',
            skiprows=3, #Removes unneccesary metadata
            usecols=[0, 1, 2, 3, 4, 5, 10, 11], #Removes unneccesary columns contaitng metadata, 
            header=None,
            names=[  #
                "UV[mL]", "UV[mAU]",
                "Conductivity[mL]", "Conductivity[mS/cm]",
                "ConcB[mL]", "ConcB[%]",
                "Fraction[mL]", "Fraction[n]"])
        return self.data

    def hep_plot(self):
        """Plots ConcB vs UV and Conductivity on the same axes."""
        if self.data is None:
            raise ValueError("Data not loaded. Load data first")

        fig, ax1 = plt.subplots()

        # Plot UV on the left y-axis
        color = 'tab:blue'
        ax1.set_xlabel("ConcB [mL]")
        ax1.set_ylabel("UV [mAU]", color=color)
        ax1.plot(self.data["ConcB[mL]"], self.data["UV[mAU]"], color=color, label="UV$_{280}$")
        ax1.tick_params(axis='y', labelcolor=color)

        # Create a second y-axis for Conductivity
        ax2 = ax1.twinx()
        color = 'tab:red'
        ax2.set_ylabel("Conductivity [mS/cm]", color=color)
        ax2.plot(self.data["ConcB[mL]"], self.data["Conductivity[mS/cm]"], color=color, label="Conductivity[mS/cm]")
        ax2.tick_params(axis='y', labelcolor=color)

        plt.title("Heparin chromatography column")
        plt.grid(False)
        fig.tight_layout()
        plt.show()

    def eluation_plot(self,title = None, x_min = None, x_max = None,y_min = None, y_max = None,
                       save_path="Data/AKTA/Figures"):
        """
        Function to plot the affinity chromatography data. It plots the UV and eluate concentration against the volume. 
        The user can specify the x-axis limits using x_min and x_max parameters, in the case that the eluate absorbance is low.
        """
        if self.data is None:
            raise ValueError("Data not loaded. Load data first")

        # Ask for title if none was provided
        if title is None:
            title = input("What should the title be? ")

        fig, ax1 = plt.subplots()

        # Plot UV on the left y-axis
        color = 'tab:blue'
        ax1.set_xlabel("mL")
        ax1.set_ylabel("UV$_{280}$[mAU]", color=color)
        ax1.plot(self.data["UV[mL]"], self.data["UV[mAU]"], color=color, label="UV$_{280}$")
        ax1.tick_params(axis='y', labelcolor=color)

        # Create a second y-axis for B concentration in %
        ax2 = ax1.twinx()
        color = 'tab:green'
        ax2.set_ylabel("Concentration Eluate [%]", color=color)
        ax2.plot(self.data["ConcB[mL]"], self.data["ConcB[%]"], color=color, label="Concentration B")
        ax2.tick_params(axis='y', labelcolor=color)

        #Sets the axis limit
        ax1.set_xlim(left=x_min, right=x_max)
        ax1.set_ylim(bottom=y_min, top=y_max)

        # Get the actual y-axis limits after applying the user's settings
        current_y_min, current_y_max = ax1.get_ylim()

        # Fraction bar height = 10% of visible y-axis
        bar_height = 0.05 * (current_y_max - current_y_min)

        # Add fraction marks
        fraction_data = self.data[["Fraction[mL]", "Fraction[n]"]].dropna()

        # Only include fractions within the plotted x-axis range
        if x_min is not None:
            fraction_data = fraction_data[fraction_data["Fraction[mL]"] >= x_min]

        if x_max is not None:
            fraction_data = fraction_data[fraction_data["Fraction[mL]"] <= x_max]

        for i, (_, row) in enumerate(fraction_data.iterrows(), start=1):
            x = row["Fraction[mL]"]
            fraction_number = str(row["Fraction[n]"]).replace("Outlet ", "")

            # Fraction bar
            ax1.vlines(
                x=x,
                ymin=0,
                ymax=bar_height,
                color="black",
                linewidth=1
            )

            # Check if fraction ID is numeric
            is_numeric = fraction_number.replace(".", "", 1).isdigit()

            # Annotate every third numeric fraction OR always annotate non-numeric fractions
            if i % 3 == 0 or not is_numeric:

                # Non-numeric labels are placed higher
                if not is_numeric:
                    text_height = bar_height * 1.5
                else:
                    text_height = bar_height

                ax1.text(
                    x,
                    text_height,
                    fraction_number,
                    ha="center",
                    va="bottom",
                    fontsize=8
                )

        ax1.set_title(title)
        plt.grid(False)
        fig.tight_layout()

        # Combine legends from  both axes
        lines_1, labels_1 = ax1.get_legend_handles_labels()
        lines_2, labels_2 = ax2.get_legend_handles_labels()
        ax1.legend(lines_1 + lines_2, labels_1 + labels_2, loc='upper left')

        save_path = Path(save_path)
        save_path.mkdir(parents=True, exist_ok=True)

        # Save figure
        filename = save_path / f"{title}.png"
        fig.savefig(filename, dpi=300, bbox_inches="tight")

        print(f"Figure saved to: {filename}")

        plt.show()

    def sec_plot(self, title=None, x_min=None, x_max=None, y_min=None, y_max=None,
                save_path="Data/AKTA/Figures", datasets=None):
        """
        Plot SEC chromatography data.

        The current object is plotted by default. Additional datasets can be
        supplied as a dictionary:
        
            datasets={
                "This protein": this_protein,
                "That protein": that_protein
            }
        """

        if self.data is None:
            raise ValueError("Data not loaded. Load data first")

        # Ask for title if none was provided
        if title is None:
            title = input("What should the title be? ")

        fig, ax1 = plt.subplots()

        ax1.set_xlabel("mL")
        ax1.set_ylabel("UV$_{280}$[mAU]")

        # If no additional datasets were supplied, just plot self
        if datasets is None:
            datasets = {"UV$_{280}$": self}

        # Plot each dataset
        for label, dataset in datasets.items():

            if dataset.data is None:
                raise ValueError(f"Data not loaded for '{label}'")

            ax1.plot(
                dataset.data["UV[mL]"],
                dataset.data["UV[mAU]"],
                label=label
            )

        # Axis limits
        if x_min is not None or x_max is not None:
            ax1.set_xlim(x_min, x_max)

        if y_min is not None or y_max is not None:
            ax1.set_ylim(y_min, y_max)

        # Legend
        ax1.legend(loc="upper left")

        save_path = Path(save_path)
        save_path.mkdir(parents=True, exist_ok=True)

        # Save figure
        filename = save_path / f"{title}.png"
        fig.savefig(filename, dpi=300, bbox_inches="tight")

        print(f"Figure saved to: {filename}")

        plt.show()




# Example usage
if __name__ == "__main__":
    analyzer = AktaVisualiser("Data/20250501 Heparin Run 5mL 25-2 001 001.csv")
    data = analyzer.read_data()
    print(data.head())
    analyzer.plot_conc_b_vs_uv_and_cond()