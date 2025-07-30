import yaml
import numpy as np
import scipy.stats as sss


def parse_file(file_path):
    params = {}
    try:
        # read data from a yaml file
        with open(file_path, "r") as fichier:
            params = yaml.safe_load(fichier)

        # Convert lists to NumPy arrays
        for key, value in params.items():
            if isinstance(value, list):
                params[key] = np.array(value)

    except FileNotFoundError:
        print(f"The file {file_path} wasn't found.")
    except Exception as e:
        print(f"An error occurred: {e}")
    return params


def create_param_file(params, file_path="param_simu_"):
    file_name = f"{file_path}.yaml"

    for key, value in params.items():
        if isinstance(value, np.ndarray):
            params[key] = value.tolist()

    try:
        with open(file_name, "w") as fichier:
            yaml.safe_dump(params, fichier, default_flow_style=None)
        print(f"File {file_name} created successfully.")
    except Exception as e:
        print(f"An error occurred: {e}")


def fitness(x, s, h):
    """
    Fitness function that calculates the post selection frequency of an allele
    with  pre-selection frequency x, selection coefficient s and dominance parameter h.

    Parameters:
    - x: Allele frequency, representing the proportion of individuals carrying the allele.
    - s: Selection parameter, measuring the strength and direction of natural selection.
    - h: Dominance parameter, describing the dominance/recessiveness of the allele.

    Returns
    - Post selection allele frequency

    fitness(x, s, h) = \Sum w_g f_g

    with
    f_g = (1-x)**2, 2x(1-x), x**2
    w_g = 1, 1+sh, 1+s
    Leading to:
    fitness(x, s, h) = (x * (1 + s * h + s * (1 - h) * x)) / (1 + 2 * s * h * x + s * (1 - 2 * h) * x**2)

    The formula calculates the relative fitness of an individual carrying the allele with frequency x
    in the population based on selection and dominance effects. Positive selection (positive s) increases
    fitness, while negative selection (negative s) decreases it.
    """
    # Calculate the fitness using the provided formula
    return (
        x
        * (1 + s * h + s * (1 - h) * x)
        / (1 + 2 * s * h * x + s * (1 - 2 * h) * x ** 2)
    )


def wf_simulator_N(x_0, VN, s, time, h):
    """
    Simulate allele frequencies under a Wright-Fisher process with varying effective population sizes.

    Parameters:
    - x_0: Initial allele frequency.
    - VN: Vector of effective population sizes for each generation.
    - s: Selection parameter.
    - time: Length of the simulation (in generations).
    - h: Dominance parameter.

     Returns:
    - An array of allele frequencies at different time points.

    This function simulates allele frequencies over time based on the Wright-Fisher model.
    It starts with an initial allele frequency (x_0) and simulates changes in allele frequencies
    over a specified number of generations (time). The simulation takes into account the varying
    population sizes (VN), selection strength (s), and dominance (h) parameters.

    The function uses a binomial random variable to simulate genetic drift and selection.
    """

    # Create an array to store allele frequencies at different time points
    frequency = np.zeros(time)
    frequency[0] = x_0  # Set the initial allele frequency

    for gen in range(time - 1):
        # Calculate the new allele frequency after selection
        proba = fitness(frequency[gen], s, h)

        # Sample in finite population (drift)
        k = sss.binom.rvs(n=VN[gen], p=proba)

        # Update with the realized allele frequency
        frequency[gen + 1] = k / VN[gen]

    return frequency


def simulate_sampling_N(x_0, VN, s, sampling_time, depth_vect, h):
    """
    Simulate sampling from a Wright-Fisher process with varying effective sizes.

    Parameters:
    - x_0: Initial allele frequency.
    - VN: Array of effective population sizes (varying over time).
    - s: Selection parameter.
    - sampling_time: List of sampling generations.
    - depth_vect: List of the number of individuals sampled at each sampling generation.
    - h: Dominance parameter.
    - u: Mutation parameter (optional, default = 0).
    - v: Mutation parameter (optional, default = 0).
    - plot: If True, plot the simulation results (optional, default = False).

    Returns:
    - An array of allele frequencies over time, a list of sampled individuals at specified generations,
      and a list of sample sizes.

    This function simulates the sampling of individuals from a Wright-Fisher process with varying
    effective population sizes over time. It starts with an initial allele frequency (x_0) and simulates
    allele frequency changes over a specified number of generations (sampling_time). At each sampling
    time, individuals are sampled from the population according to the specified sample sizes (depth_vect).

    The function returns an array of allele frequencies over time, a list of sampled individuals at the
    specified generations, and a list of corresponding sample sizes.

    Note: The optional 'plot' parameter can be used to visualize the simulation results if set to True.
    """

    # Determine the maximum time for the simulation based on sampling times
    time = max(sampling_time) + 1

    # Simulate allele frequencies over time with varying effective sizes
    res = wf_simulator_N(x_0, VN, s, time, h)

    # Initialize lists to store sampled individuals, sample sizes per sampling time
    sampling_res = []
    sampling_size = []

    # Simulate sampling at each specified sampling time
    for i in range(len(sampling_time)):

        # Obtain the sample size
        size = depth_vect[i]

        # Sample individuals from the population
        indiv = sss.binom.rvs(n=size, p=res[sampling_time[i]])

        # Append the sampled individual count, sample size per sampling time
        sampling_res.append(indiv)
        sampling_size.append(size)
    return res, sampling_res, sampling_size


def save_traj_csv(sampling_count, sampling_size, filename="trajectory"):
    # Prepare the data
    data = zip(sampling_count, sampling_size)
    csv_file_path = filename + ".csv"

    # Open the file in write mode, which will overwrite the file if it exists
    with open(csv_file_path, mode="w") as file:
        # Write the header
        file.write("sampling_count,sampling_size\n")

        # Write the data
        for sc, ss in data:
            file.write(f"{sc},{ss}\n")


def save_traj_baypass(sampling_count, sampling_size, filename="trajectory"):
    baypass_file_path = filename + ".baypass"
    try:
        with open(baypass_file_path, "r") as file:
            baypass_content = file.read()
    except:
        baypass_content = ""
    for i in range(len(sampling_count)):
        for j in range(len(sampling_count[i])):
            baypass_content += (
                str(sampling_count[i][j])
                + " "
                + str(sampling_size[i][j] - sampling_count[i][j])
                + " "
            )
        baypass_content = baypass_content[:-1]
        baypass_content += "\n"
    baypass_file_path = filename + ".genobaypass"
    with open(baypass_file_path, "w") as text_file:
        text_file.write(baypass_content)


def create_trajectories_simulations(
    file_path, filename, seed, file_type="baypass"
):
    data = parse_file(file_path)
    x0 = data["x0"]
    sampling_time = data["sampling_time"]
    depth_vect = data["depth_vect"]
    s = data["s"]
    h = data["h"]
    nbr_traj = data["nrep"]
    p = data["proportion_sel"]
    count = []
    depth = []
    np.random.seed(seed)
    if len(depth_vect) != len(sampling_time):
        print(len(depth_vect), len(sampling_time))
        raise ValueError("The length of depth_vect should be the same as sampling_time")
    if x0 == "uniform":
        x0 = np.random.rand(1, nbr_traj)[0]  # x0 can be equal to 1 or 0
    else:
        x0 = np.full(nbr_traj, x0)
    VN = np.ones(np.amax(sampling_time), dtype="int64") * data["N"]

    for i in range(int(nbr_traj * p)):
        x0_sim = x0[i]
        res, sampling_count, sampling_size = simulate_sampling_N(
            x0_sim, VN, s, sampling_time, depth_vect, h
        )
        count.append(sampling_count)
        depth.append(sampling_size)
    for i in range(int(nbr_traj * p), nbr_traj):
        x0_sim = x0[i]
        res, sampling_count, sampling_size = simulate_sampling_N(
            x0_sim, VN, 0, sampling_time, depth_vect, h
        )
        count.append(sampling_count)
        depth.append(sampling_size)

    if file_type == "csv":
        save_traj_csv(count, depth, filename=filename)
    else:
        save_traj_baypass(count, depth, filename=filename)
