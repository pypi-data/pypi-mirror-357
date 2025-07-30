# Model: NGBoost Regressor with Distribution output
from ngboost import NGBRegressor
from sklearn.model_selection import train_test_split

# Template Placeholders
TEMPLATE_PARAMS = {
    "features": ['bcut2d_logplow', 'numradicalelectrons', 'smr_vsa5', 'fr_lactam', 'fr_morpholine', 'fr_aldehyde', 'slogp_vsa1', 'fr_amidine', 'bpol', 'fr_ester', 'fr_azo', 'kappa3', 'peoe_vsa5', 'fr_ketone_topliss', 'vsa_estate9', 'estate_vsa9', 'bcut2d_mrhi', 'fr_ndealkylation1', 'numrotatablebonds', 'minestateindex', 'fr_quatn', 'peoe_vsa3', 'fr_epoxide', 'fr_aniline', 'minpartialcharge', 'fr_nitroso', 'fpdensitymorgan2', 'fr_oxime', 'fr_sulfone', 'smr_vsa1', 'kappa1', 'fr_pyridine', 'numaromaticrings', 'vsa_estate6', 'molmr', 'estate_vsa1', 'fr_dihydropyridine', 'vsa_estate10', 'fr_alkyl_halide', 'chi2n', 'fr_thiocyan', 'fpdensitymorgan1', 'fr_unbrch_alkane', 'slogp_vsa9', 'chi4n', 'fr_nitro_arom', 'fr_al_oh', 'fr_furan', 'fr_c_s', 'peoe_vsa8', 'peoe_vsa14', 'numheteroatoms', 'fr_ndealkylation2', 'maxabspartialcharge', 'vsa_estate2', 'peoe_vsa7', 'apol', 'numhacceptors', 'fr_tetrazole', 'vsa_estate1', 'peoe_vsa9', 'naromatom', 'bcut2d_chghi', 'fr_sh', 'fr_halogen', 'slogp_vsa4', 'fr_benzodiazepine', 'molwt', 'fr_isocyan', 'fr_prisulfonamd', 'maxabsestateindex', 'minabsestateindex', 'peoe_vsa11', 'slogp_vsa12', 'estate_vsa5', 'numaliphaticcarbocycles', 'bcut2d_mwlow', 'slogp_vsa7', 'fr_allylic_oxid', 'fr_methoxy', 'fr_nh0', 'fr_coo2', 'fr_phenol', 'nacid', 'nbase', 'chi3v', 'fr_ar_nh', 'fr_nitrile', 'fr_imidazole', 'fr_urea', 'bcut2d_mrlow', 'chi1', 'smr_vsa6', 'fr_aryl_methyl', 'narombond', 'fr_alkyl_carbamate', 'fr_piperzine', 'exactmolwt', 'qed', 'chi0n', 'fr_sulfonamd', 'fr_thiazole', 'numvalenceelectrons', 'fr_phos_acid', 'peoe_vsa12', 'fr_nh1', 'fr_hdrzine', 'fr_c_o_nocoo', 'fr_lactone', 'estate_vsa6', 'bcut2d_logphi', 'vsa_estate7', 'peoe_vsa13', 'numsaturatedcarbocycles', 'fr_nitro', 'fr_phenol_noorthohbond', 'rotratio', 'fr_barbitur', 'fr_isothiocyan', 'balabanj', 'fr_arn', 'fr_imine', 'maxpartialcharge', 'fr_sulfide', 'slogp_vsa11', 'fr_hoccn', 'fr_n_o', 'peoe_vsa1', 'slogp_vsa6', 'heavyatommolwt', 'fractioncsp3', 'estate_vsa8', 'peoe_vsa10', 'numaliphaticrings', 'fr_thiophene', 'maxestateindex', 'smr_vsa10', 'labuteasa', 'smr_vsa2', 'fpdensitymorgan3', 'smr_vsa9', 'slogp_vsa10', 'numaromaticheterocycles', 'fr_nh2', 'fr_diazo', 'chi3n', 'fr_ar_coo', 'slogp_vsa5', 'fr_bicyclic', 'fr_amide', 'estate_vsa10', 'fr_guanido', 'chi1n', 'numsaturatedrings', 'fr_piperdine', 'fr_term_acetylene', 'estate_vsa4', 'slogp_vsa3', 'fr_coo', 'fr_ether', 'estate_vsa7', 'bcut2d_chglo', 'fr_oxazole', 'peoe_vsa6', 'hallkieralpha', 'peoe_vsa2', 'chi2v', 'nocount', 'vsa_estate5', 'fr_nhpyrrole', 'fr_al_coo', 'bertzct', 'estate_vsa11', 'minabspartialcharge', 'slogp_vsa8', 'fr_imide', 'kappa2', 'numaliphaticheterocycles', 'numsaturatedheterocycles', 'fr_hdrzone', 'smr_vsa4', 'fr_ar_n', 'nrot', 'smr_vsa8', 'slogp_vsa2', 'chi4v', 'fr_phos_ester', 'fr_para_hydroxylation', 'smr_vsa3', 'nhohcount', 'estate_vsa2', 'mollogp', 'tpsa', 'fr_azide', 'peoe_vsa4', 'numhdonors', 'fr_al_oh_notert', 'fr_c_o', 'chi0', 'fr_nitro_arom_nonortho', 'vsa_estate3', 'fr_benzene', 'fr_ketone', 'vsa_estate8', 'smr_vsa7', 'fr_ar_oh', 'fr_priamide', 'ringcount', 'estate_vsa3', 'numaromaticcarbocycles', 'bcut2d_mwhi', 'chi1v', 'heavyatomcount', 'vsa_estate4', 'chi0v'],
    "target": "udm_asy_res_value",
    "train_all_data": True
}

from io import StringIO
import json
import argparse
import joblib
import os
import pandas as pd


# Function to check if dataframe is empty
def check_dataframe(df: pd.DataFrame, df_name: str) -> None:
    """Check if the DataFrame is empty and raise an error if so."""
    if df.empty:
        msg = f"*** The training data {df_name} has 0 rows! ***STOPPING***"
        print(msg)
        raise ValueError(msg)


# Function to match DataFrame columns to model features (case-insensitive)
def match_features_case_insensitive(df: pd.DataFrame, model_features: list) -> pd.DataFrame:
    """Match and rename DataFrame columns to match the model's features, case-insensitively."""
    # Create a set of exact matches from the DataFrame columns
    exact_match_set = set(df.columns)

    # Create a case-insensitive map of DataFrame columns
    column_map = {col.lower(): col for col in df.columns}
    rename_dict = {}

    # Build a dictionary for renaming columns based on case-insensitive matching
    for feature in model_features:
        if feature in exact_match_set:
            rename_dict[feature] = feature
        elif feature.lower() in column_map:
            rename_dict[column_map[feature.lower()]] = feature

    # Rename columns in the DataFrame to match model features
    return df.rename(columns=rename_dict)


# TRAINING SECTION
#
# This section (__main__) is where SageMaker will execute the training job
# and save the model artifacts to the model directory.
#
if __name__ == "__main__":
    # Template Parameters
    features = TEMPLATE_PARAMS["features"]
    target = TEMPLATE_PARAMS["target"]
    train_all_data = TEMPLATE_PARAMS["train_all_data"]
    validation_split = 0.2

    # Script arguments for input/output directories
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-dir", type=str, default=os.environ.get("SM_MODEL_DIR", "/opt/ml/model"))
    parser.add_argument("--train", type=str, default=os.environ.get("SM_CHANNEL_TRAIN", "/opt/ml/input/data/train"))
    parser.add_argument(
        "--output-data-dir", type=str, default=os.environ.get("SM_OUTPUT_DATA_DIR", "/opt/ml/output/data")
    )
    args = parser.parse_args()

    # Load training data from the specified directory
    training_files = [
        os.path.join(args.train, file)
        for file in os.listdir(args.train) if file.endswith(".csv")
    ]
    df = pd.concat([pd.read_csv(file, engine="python") for file in training_files])

    # Check if the DataFrame is empty
    check_dataframe(df, "training_df")

    # Training data split logic
    if train_all_data:
        # Use all data for both training and validation
        print("Training on all data...")
        df_train = df.copy()
        df_val = df.copy()
    elif "training" in df.columns:
        # Split data based on a 'training' column if it exists
        print("Splitting data based on 'training' column...")
        df_train = df[df["training"]].copy()
        df_val = df[~df["training"]].copy()
    else:
        # Perform a random split if no 'training' column is found
        print("Splitting data randomly...")
        df_train, df_val = train_test_split(df, test_size=validation_split, random_state=42)

    # Create and train the NGBoost Regression model optimized for noisy molecular data
    model = NGBRegressor(
        n_estimators=1000,  # More trees for noisy data (default 500)
        learning_rate=0.01,  # Slower learning to avoid overfitting (default 0.01)
        minibatch_frac=0.8,  # Use 80% of data per iteration for robustness (default 1.0)
        col_sample=0.8,  # Use 80% of features per tree (helps with 17 features)
        tol=1e-5,  # Tighter convergence tolerance (default 1e-4)
        random_state=42,  # For reproducibility
        verbose=False
    )

    # Prepare features and targets for training
    X_train = df_train[features]
    X_val = df_val[features]
    y_train = df_train[target]
    y_val = df_val[target]

    # Train the model using the training data
    model.fit(X_train, y_train)

    # Save the trained model and any necessary assets
    joblib.dump(model, os.path.join(args.model_dir, "model.joblib"))

    # Save the feature list to validate input during predictions
    with open(os.path.join(args.model_dir, "feature_columns.json"), "w") as fp:
        json.dump(features, fp)


#
# Inference Section
#
def model_fn(model_dir):
    """Load and return the model from the specified directory."""
    return joblib.load(os.path.join(model_dir, "model.joblib"))


def input_fn(input_data, content_type):
    """Parse input data and return a DataFrame."""
    if not input_data:
        raise ValueError("Empty input data is not supported!")

    # Decode bytes to string if necessary
    if isinstance(input_data, bytes):
        input_data = input_data.decode("utf-8")

    if "text/csv" in content_type:
        return pd.read_csv(StringIO(input_data))
    elif "application/json" in content_type:
        return pd.DataFrame(json.loads(input_data))  # Assumes JSON array of records
    else:
        raise ValueError(f"{content_type} not supported!")


def output_fn(output_df, accept_type):
    """Supports both CSV and JSON output formats."""
    if "text/csv" in accept_type:
        csv_output = output_df.fillna("N/A").to_csv(index=False)  # CSV with N/A for missing values
        return csv_output, "text/csv"
    elif "application/json" in accept_type:
        return output_df.to_json(orient="records"), "application/json"  # JSON array of records (NaNs -> null)
    else:
        raise RuntimeError(f"{accept_type} accept type is not supported by this script.")


def predict_fn(df, model):
    """Make predictions or apply transformations using the model and return the DataFrame with results."""
    model_dir = os.environ.get("SM_MODEL_DIR", "/opt/ml/model")

    # Load feature columns from the saved file
    with open(os.path.join(model_dir, "feature_columns.json")) as fp:
        model_features = json.load(fp)

    # Match features in a case-insensitive manner
    matched_df = match_features_case_insensitive(df, model_features)

    # NGBoost predict returns distribution objects
    y_dists = model.pred_dist(matched_df[model_features])

    # Extract parameters from distribution
    dist_params = y_dists.params

    # Extract mean and std from distribution parameters
    df["prediction"] = dist_params['loc']  # mean
    df["prediction_std"] = dist_params['scale']  # standard deviation

    # Add 95% prediction intervals using ppf (percent point function)
    df["q_025"] = y_dists.ppf(0.025)  # 2.5th percentile
    df["q_975"] = y_dists.ppf(0.975)  # 97.5th percentile

    # Add 50% prediction intervals
    df["q_25"] = y_dists.ppf(0.25)   # 25th percentile
    df["q_75"] = y_dists.ppf(0.75)   # 75th percentile

    # Return the modified DataFrame
    return df
