class Lambert:
    def __init__(
        self,
        absorbance: float,
        molar_extinction_coefficient: float = None,
        mass_extinction_coefficient: float = None,
    ):
        """
        Initialize the Lambert instance with absorbance and extinction coefficients.

        Parameters:
        absorbance (float): The absorbance of the sample.
        molar_extinction_coefficient (float, optional): The molar extinction coefficient (in M⁻¹ cm⁻¹). Defaults to None.
        mass_extinction_coefficient (float, optional): The mass extinction coefficient (in (mg/mL)⁻¹ cm⁻¹). Defaults to None.
        """
        self.absorbance = absorbance
        self.molar_extinction_coefficient = molar_extinction_coefficient
        self.mass_extinction_coefficient = mass_extinction_coefficient

        # Initialize concentrations as None
        self.molar_concentration = None
        self.mg_per_mL_concentration = None

        # Validate and calculate molar concentration
        if self.molar_extinction_coefficient is not None:
            if self.molar_extinction_coefficient <= 0:
                raise ValueError("Molar extinction coefficient must be a positive value.")
            self.molar_concentration = self.calculate_molar_concentration()

        # Validate and calculate mg/mL concentration
        if self.mass_extinction_coefficient is not None:
            if self.mass_extinction_coefficient <= 0:
                raise ValueError("Mass extinction coefficient must be a positive value.")
            self.mg_per_mL_concentration = self.calculate_mg_per_mL_concentration()

        # Print available results
        if self.molar_concentration is not None:
            print(f"Molar Concentration: {self.molar_concentration:.4f} M")
        if self.mg_per_mL_concentration is not None:
            print(f"Concentration: {self.mg_per_mL_concentration:.4f} mg/mL")

    def calculate_molar_concentration(self, path_length: float = 1.0) -> float:
        """
        Calculate the molar concentration using the molar extinction coefficient.

        Parameters:
        path_length (float): The path length of the cuvette in cm. Default is 1.0 cm.

        Returns:
        float: The molar concentration in M (mol/L).

        Raises:
        ValueError: If molar_extinction_coefficient is not provided.
        """
        if self.molar_extinction_coefficient is None:
            raise ValueError("Molar extinction coefficient is required for this calculation.")
        if path_length <= 0:
            raise ValueError("Path length must be a positive value.")

        return self.absorbance / (self.molar_extinction_coefficient * path_length)

    def calculate_mg_per_mL_concentration(self, path_length: float = 1.0) -> float:
        """
        Calculate the concentration in mg/mL using the mass extinction coefficient.

        Parameters:
        path_length (float): The path length of the cuvette in cm. Default is 1.0 cm.

        Returns:
        float: The concentration in mg/mL.

        Raises:
        ValueError: If mass_extinction_coefficient is not provided.
        """
        if self.mass_extinction_coefficient is None:
            raise ValueError("Mass extinction coefficient is required for this calculation.")
        if path_length <= 0:
            raise ValueError("Path length must be a positive value.")

        return self.absorbance / (self.mass_extinction_coefficient * path_length)