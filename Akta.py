import csv
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

def akta_parser(filepath):
    """
    Parse an ÄKTA CSV export.

    Structure:
        row 1 -> ignored
        row 2 -> parameter
        row 3 -> subparameter / unit
        row 4+ -> data

    The number of columns may vary.
    The delimiter is a tab.
    """

    # ---------------------------------------------------------
    # 1. Read the raw file and extract rows
    # ---------------------------------------------------------

    with open(filepath, "r", encoding="utf-16") as f:

        reader = csv.reader(
            f,
            delimiter="\t"
        )

        rows = list(reader)

    parameter_row = rows[1]
    subparameter_row = rows[2]
    data_rows = rows[3:]

    # Fill blank parameter names with the previous parameter
    for i in range(1, len(parameter_row)):

        if parameter_row[i] == "":
            parameter_row[i] = parameter_row[i - 1]

    # ---------------------------------------------------------
    # 2. Determine number of columns
    # ---------------------------------------------------------

    n_columns = max(
        len(parameter_row),
        len(subparameter_row),
        *(len(row) for row in data_rows)
    )

    # ---------------------------------------------------------
    # 3. Pad headers and data
    # ---------------------------------------------------------

    parameter_row = parameter_row + [
        ""
    ] * (n_columns - len(parameter_row))

    subparameter_row = subparameter_row + [
        ""
    ] * (n_columns - len(subparameter_row))

    data = []

    for row in data_rows:

        row = row + [""] * (
            n_columns - len(row)
        )

        data.append(row[:n_columns])

    # ---------------------------------------------------------
    # 4. Create MultiIndex and dataframe
    # ---------------------------------------------------------

    columns = pd.MultiIndex.from_arrays(
        [
            parameter_row,
            subparameter_row
        ],
        names=[
            "parameter",
            "subparameter"
        ]
    )

    df = pd.DataFrame(
        data,
        columns=columns
    )

    # ---------------------------------------------------------
    # 5. Convert columns to numeric where possible
    # ---------------------------------------------------------

    converted_columns = []

    for i in range(df.shape[1]):

        column = df.iloc[:, i]

        converted = pd.to_numeric(
            column,
            errors="coerce"
        )

        if converted.notna().any():
            converted_columns.append(converted)

        else:
            converted_columns.append(column)

    # Rebuild dataframe
    df = pd.concat(
        converted_columns,
        axis=1
    )

    df.columns = columns

    return df

class AktaVisualiser:

    def __init__(self,df):
        if df is None:
            raise ValueError("No data has been provided")

        self.df = df


    def sec_plot(self, title=None, x_min=None, x_max=None,
        y_min=None, y_max=None, save_path="Data/AKTA/Figures",
        colours=None, datasets=None, fraction_marks="all",
        label = "UV", legend_location = "upper left"):
        """
        Plot chromatography data from an ÄKTA dataframe.
        Especially useful for SEC.

        Parameters
        ----------
        df : pandas.DataFrame
            Dataframe returned by parse_akta_csv().

        title : str, optional
            Figure title. If None, asks for a title.

        x_min, x_max : float, optional
            Sets X-axis limits for zoom function.

        y_min, y_max : float, optional
            Y-axis limits for zoom function.

        save_path : str or Path
            Directory where the figure is saved.

        colours : str or dict, optional
            Colour of the plotted dataset(s).

            For one colour for all datasets:
                colours="orange"

            For individual colours:
                colours={
                    "Sample A": "blue",
                    "Sample B": "red"}
        
        legend_location : dict, optional
            Used to specify the location of the legend
            upper left corner is the default.

        label : dict, optinal
            Specify the labe lfor the legend, default is UV

        datasets : dict, optional
            Additional datasets to plot.

            Example:
                datasets={
                    "Protein A": df1,
                    "Protein B": df2
                }

            Each value must be a dataframe returned by parse_akta_csv().

        fraction_marks : str, optional
            Determines how many of the fraction labels will be shown.
            Options are "all" or "thirds".
        """

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

        ax1.set_xlabel("Elution Volume [mL]")
        ax1.set_ylabel("UV$_{280}$ [mAU]")

        # ---------------------------------------------------------
        # 5. Plot datasets and axis limits
        # ---------------------------------------------------------

        for label, dataset in datasets.items():

            if dataset is None:
                raise ValueError(
                    f"Data not provided for '{label}'"
                )

            x = dataset[("UV", "ml")]
            y = dataset[("UV", "mAU")]

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

        # Get actual y-axis limits AFTER applying user settings
        current_y_min, current_y_max = ax1.get_ylim()

        # ---------------------------------------------------------
        # 6. Fraction marks
        # ---------------------------------------------------------
        if fraction_marks != "None":

                    fraction_data = self.df[
                        [
                            ("Fraction", "ml"),
                            ("Fraction", "Fraction")
                        ]
                    ].dropna()

                    # Only include fractions within plotted x-axis range

                    if x_min is not None:
                        fraction_data = fraction_data[
                            fraction_data[("Fraction", "ml")] >= x_min
                        ]

                    if x_max is not None:
                        fraction_data = fraction_data[
                            fraction_data[("Fraction", "ml")] <= x_max
                        ]

                    # Fraction bar height as a fraction of the physical plot height
                    bar_height = 0.05

                    # x = data coordinates
                    # y = axes coordinates (0 = bottom of plot, 1 = top)
                    transform = ax1.get_xaxis_transform()

                    for i, (_, row) in enumerate(
                        fraction_data.iterrows(),
                        start=1
                    ):

                        x = row[("Fraction", "ml")]

                        fraction_number = str(
                            row[("Fraction", "Fraction")]
                        ).replace("Outlet ", "")

                        # -----------------------------------------------------
                        # Fraction bar
                        # -----------------------------------------------------

                        ax1.plot(
                            [x, x],
                            [0, bar_height],
                            transform=transform,
                            color="black",
                            linewidth=1
                        )

                        # -----------------------------------------------------
                        # Fraction label
                        # -----------------------------------------------------

                        is_numeric = fraction_number.replace(
                            ".", "", 1
                        ).isdigit()

                        # Determine whether this fraction gets a label
                        show_label = False

                        if fraction_marks == "all":
                            show_label = True

                        elif isinstance(fraction_marks, int):
                            if fraction_marks > 0 and i % fraction_marks == 0:
                                show_label = True

                        # Always show non-numeric labels
                        if not is_numeric:
                            show_label = True

                        if show_label:

                            if not is_numeric:
                                text_height = bar_height * 1.5

                            else:
                                text_height = bar_height

                            # Format 2.0 -> 2
                            if is_numeric:
                                fraction_number = (
                                    str(int(float(fraction_number)))
                                    if float(fraction_number).is_integer()
                                    else fraction_number
                                )

                            ax1.text(
                                x,
                                text_height,
                                fraction_number,
                                transform=transform,
                                ha="center",
                                va="bottom",
                                fontsize=8
                            )
        else:
            pass


        # ---------------------------------------------------------
        # 7. Title, formatting and legend
        # ---------------------------------------------------------

        ax1.set_title(title, pad=10)

        ax1.grid(False)
        # Legend
        ax1.legend(
            loc= legend_location
        )

        # ---------------------------------------------------------
        # 8. Layout
        # ---------------------------------------------------------

        fig.tight_layout()

        # ---------------------------------------------------------
        # 9. Save figure
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

    def affinity_plot(self, title=None, x_min=None, x_max=None,
        y_min=None, y_max=None, fraction_marks="all",  legend_location = "upper left",
        save_path="Data/AKTA/Figures"):
        """
        Plot affinity chromatography data from an ÄKTA dataframe.

        UV is plotted on the left y-axis and eluate concentration
        (Conc B) is plotted on the right y-axis.

        Parameters
        ----------
        df : pandas.DataFrame
            Dataframe returned by parse_akta_csv().

        title : str, optional
            Figure title. If None, asks for a title.

        x_min, x_max : float, optional
            X-axis limits.

        y_min, y_max : float, optional
            UV y-axis limits.
        
        legend_location : dict, optional
            Specifies the legend location, upper left is the default.

        save_path : str or Path
            Directory where the figure is saved.
        """

        # ---------------------------------------------------------
        # 1. Check input
        # ---------------------------------------------------------

        if self.df is None:
            raise ValueError("Data not provided.")

        # Ask for title if none was provided
        if title is None:
            title = input("What should the title be? ")

        # ---------------------------------------------------------
        # 2. Create and plot UV
        # ---------------------------------------------------------

        fig, ax1 = plt.subplots()

        color = "tab:blue"

        ax1.set_xlabel("mL")
        ax1.set_ylabel(
            "UV$_{280}$ [mAU]",
            color=color
        )

        ax1.plot(
            self.df[("UV", "ml")],
            self.df[("UV", "mAU")],
            color=color,
            label="UV$_{280}$"
        )

        ax1.tick_params(
            axis="y",
            labelcolor=color
        )

        # ---------------------------------------------------------
        # 3. Plot concentration on right y-axis
        # ---------------------------------------------------------

        ax2 = ax1.twinx()

        color = "tab:green"

        ax2.set_ylabel(
            "Concentration Eluate [%]",
            color=color
        )

        ax2.plot(
            self.df[("ConcB", "ml")],
            self.df[("ConcB", "%B")],
            color=color,
            label="Concentration B"
        )

        ax2.tick_params(
            axis="y",
            labelcolor=color
        )

        # ---------------------------------------------------------
        # 4. Set axis limits
        # ---------------------------------------------------------

        if x_min is not None or x_max is not None:
            ax1.set_xlim(x_min, x_max)

        if y_min is not None or y_max is not None:
            ax1.set_ylim(y_min, y_max)

        # ---------------------------------------------------------
        # 5. Fraction marks
        # ---------------------------------------------------------
        if fraction_marks != "None":

            fraction_data = self.df[
                [
                    ("Fraction", "ml"),
                    ("Fraction", "Fraction")
                ]
            ].dropna()

            # Only include fractions within plotted x-axis range

            if x_min is not None:
                fraction_data = fraction_data[
                    fraction_data[("Fraction", "ml")] >= x_min
                ]

            if x_max is not None:
                fraction_data = fraction_data[
                    fraction_data[("Fraction", "ml")] <= x_max
                ]

            # Fraction bar height as a fraction of the physical plot height
            bar_height = 0.05

            # x = data coordinates
            # y = axes coordinates (0 = bottom of plot, 1 = top)
            transform = ax1.get_xaxis_transform()

            for i, (_, row) in enumerate(
                fraction_data.iterrows(),
                start=1
            ):

                x = row[("Fraction", "ml")]

                fraction_number = str(
                    row[("Fraction", "Fraction")]
                ).replace("Outlet ", "")

                # -----------------------------------------------------
                # Fraction bar
                # -----------------------------------------------------

                ax1.plot(
                    [x, x],
                    [0, bar_height],
                    transform=transform,
                    color="black",
                    linewidth=1
                )

                # -----------------------------------------------------
                # Fraction label
                # -----------------------------------------------------

                is_numeric = fraction_number.replace(
                    ".", "", 1
                ).isdigit()

                # Determine whether this fraction gets a label
                show_label = False

                if fraction_marks == "all":
                    show_label = True

                elif isinstance(fraction_marks, int):
                    if fraction_marks > 0 and i % fraction_marks == 0:
                        show_label = True

                # Always show non-numeric labels
                if not is_numeric:
                    show_label = True

                if show_label:

                    if not is_numeric:
                        text_height = bar_height * 1.5

                    else:
                        text_height = bar_height

                    # Format 2.0 -> 2
                    if is_numeric:
                        fraction_number = (
                            str(int(float(fraction_number)))
                            if float(fraction_number).is_integer()
                            else fraction_number
                        )

                    ax1.text(
                        x,
                        text_height,
                        fraction_number,
                        transform=transform,
                        ha="center",
                        va="bottom",
                        fontsize=8
                    )

        else:
            pass
        # ---------------------------------------------------------
        # 6. Title, formatting and legend
        # ---------------------------------------------------------

        ax1.set_title(title, pad=10)

        ax1.grid(False)

        lines_1, labels_1 = ax1.get_legend_handles_labels()
        lines_2, labels_2 = ax2.get_legend_handles_labels()

        ax1.legend(
            lines_1 + lines_2,
            labels_1 + labels_2,
            loc = legend_location)

        # ---------------------------------------------------------
        # 7. Layout and save
        # ---------------------------------------------------------

        fig.tight_layout()

        save_path = Path(save_path)
        save_path.mkdir(
            parents=True,
            exist_ok=True)

        filename = save_path / f"{title}.png"
        fig.savefig(
            filename,
            dpi=300,
            bbox_inches="tight")

        print(f"Figure saved to: {filename}")

        plt.show()
