import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path


class GrowthCurveVisualiser:
    def __init__(self, filename):
        self.filename = filename
        self.time = []
        self.od600 = []

        self.read_data()

    def read_data(self):
        data = pd.read_csv(self.filename)

        self.time = data["Time [h]"].tolist()
        self.od600 = data["OD600"].tolist()

    @staticmethod
    def create_data_file(name=None,time=None, od600=None, sample_volumes=None):
        """
        Function to create a CSV file for growth curve data. It prompts the user for time, OD600, and sample volume data points,
        calculates the resuspend volumes, and saves the data to a CSV file.
        """

        if name is None:
            name = input("Enter a name for the experiment: ")

        if time is None:
            time = input("What are your time data points?")
            time = [float(x.strip()) for x in time.split(",")]

        if od600 is None:
            od600 = input("What are your OD600 data points? ")
            od600 = [float(x.strip()) for x in od600.split(",")]

        if sample_volumes is None:
            sample_volumes = input("What are the sample volumes? ")
            sample_volumes = [float(x.strip()) for x in sample_volumes.split(",")]
            
        
        if not (len(time) == len(od600) == len(sample_volumes)):
            print(
                "Error: Time, OD600, and sample volumes "
                "must have the same number of data points."
            )
            return

        resuspend_volumes = [
            (od * sample_volume) / 8
            for od, sample_volume in zip(od600, sample_volumes)
        ]

        data = pd.DataFrame({
            "Time [h]": time,
            "OD600": od600,
            "Sample Volume": sample_volumes,
            "Resuspend Volume": resuspend_volumes
        })

        folder = Path("Data") / "Growth"
        folder.mkdir(parents=True, exist_ok=True)

        filename = folder / f"{name}.csv"

        data.to_csv(filename, index=False)

        print(f"Data saved to {filename}")

    def plot(self, save_path="Data/Growth/Plots"):
        fig, ax = plt.subplots()

        ax.plot(self.time, self.od600, marker="o")

        ax.set_xlabel("Time [h]")
        ax.set_ylabel("OD600")
        ax.set_title("Growth curve")
        ax.grid(True)

        # Create save folder
        save_path = Path(save_path)
        save_path.mkdir(parents=True, exist_ok=True)

        # Create filename based on input CSV
        filename = save_path / f"{Path(self.filename).stem}.png"

        # Save figure
        fig.savefig(filename, dpi=300, bbox_inches="tight")

        print(f"Figure saved to: {filename}")

        plt.show()
        plt.close(fig)