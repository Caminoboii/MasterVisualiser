import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

def fluro_parser(file_path):
    '''
    Parses a file containing flurosence spectrscopy measurements
    from a JASCO fluoremeter
    '''

    df = pd.read_csv(
        file_path,
        encoding = "ASCII",
        sep = "\t",
        skiprows =  54, #Metadata
        header = None,
        names = ["Wavelength[nm]", "Intensity[AU]"])

    return df

class Fluoroesence_spectroscopy_visualiser:

    def __init__(self,df):
        if df is None:
            raise ValueError("No data has been provided")

        self.df = df

    def fluroesence_plot(self, title=None, x_min=None, x_max=None,
        y_min=None, y_max=None, save_path="Data/Fluoro/Figures",
        colours=None, datasets=None,
        label = "Empty", legend_location = "upper left"):
        '''
        Plot for visualising the full emission spectrum
        '''

        # ---------------------------------------------------------
        # 1. Check input
        # ---------------------------------------------------------

        if self.df is None:
                raise ValueError("Data not provided.")
    
        # Ask for title if none was provided
        if title is None:
                title = input("What should the title be? ")

        # ---------------------------------------------------------
        # 2. Set datasets
        # ---------------------------------------------------------

        if datasets is None:
            datasets = {
                label: self.df
            }

        # ---------------------------------------------------------
        # 3. Set colours
        # ---------------------------------------------------------

        if colours is None:
            colours = {}

        elif isinstance(colours, str):
            colours = {
                label: colours
                for label in datasets
            }

        # ---------------------------------------------------------
        # 4. Create plot
        # ---------------------------------------------------------

        fig, ax1 = plt.subplots()

        ax1.set_xlabel("Wavelength [nm]]")
        ax1.set_ylabel("Intensity [AU]")

        # ---------------------------------------------------------
        # 5. Plot datasets and axis limits
        # ---------------------------------------------------------

        for label, dataset in datasets.items():

            if dataset is None:
                raise ValueError(
                    f"Data not provided for '{label}'"
                )

            x = dataset[("Wavelength[nm]")]
            y = dataset[("Intensity[AU]")]

            ax1.plot(
                x,
                y,
                label=label,
                color=colours.get(label)
            )

        if x_min is not None or x_max is not None:
            ax1.set_xlim(x_min, x_max)

        if y_min is not None or y_max is not None:
            ax1.set_ylim(y_min, y_max)

       # ---------------------------------------------------------
        # 6. Title, formatting, legend and layout
        # ---------------------------------------------------------

        ax1.set_title(title, pad=10)

        ax1.grid(False)
        # Legend
        ax1.legend(
            loc= legend_location
        )

        fig.tight_layout()

        # ---------------------------------------------------------
        # 8. Save figure
        # ---------------------------------------------------------

        save_path = Path(save_path)

        save_path.mkdir(
            parents=True,
            exist_ok=True
        )

        filename = save_path / f"{title}.png"

        fig.savefig(
            filename,
            dpi=300,
            bbox_inches="tight"
        )

        print(f"Figure saved to: {filename}")

        plt.show()


#    def wavelength_plot:
    '''
    Plot for visulasing the change in intensity at 
    1 wavelength, for instance during a titration
    '''
