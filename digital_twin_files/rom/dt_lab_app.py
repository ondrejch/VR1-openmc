# File to create a Streamlit app for the digital_twin_lab.py exercises. 
# This app will have two main widgets: one for predicting k-effective and another for visualizing the reconstructed flux from the ROM. 
# The app will load the training data, train the models, and allow users to input parameters to see predictions in real-time.

import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import glob, re
from sklearn.metrics import mean_squared_error
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import PolynomialFeatures
import sklearn.ensemble as ensemble
from sklearn.linear_model import LinearRegression
import sklearn.neural_network as nn

NX, NY, NZ, NG = 120, 120, 70, 2

@st.cache_data
def load_flux_data(file_path):
    with np.load(file_path) as data:
        thermal = data['thermal_flux']
        fast = data['fast_flux']
        thermal_3d = thermal.reshape((NZ, NY, NX))
        fast_3d = fast.reshape((NZ, NY, NX))
        return np.stack([thermal_3d, fast_3d], axis=-1)

@st.cache_data
def extract_keff(df, folder):
    vals = []
    for case in df['case_id']:
        path = f"{folder}/results_case_{int(case)}.npz"
        with np.load(path) as d:
            vals.append(float(d['keff']))
    return np.array(vals)

@st.cache_data
def prepare_data(train_folder='VR1_DT_Lab_Training_Data', test_folder='VR1_DT_Lab_Test_Data'):
    train_df = pd.read_csv(f"{train_folder}/training_set.csv")
    test_df = pd.read_csv(f"{test_folder}/test_set.csv")
    features = [
        'cr1_height', 'cr2_height',
        'dummy_water_density_multiplier', 'fuel_assembly_water_density_multiplier'
    ]
    X_train = train_df[features].values
    X_test = test_df[features].values
    y_train_keff = extract_keff(train_df, train_folder)
    y_test_keff = extract_keff(test_df, test_folder)
    return train_df, test_df, X_train, X_test, y_train_keff, y_test_keff

@st.cache_resource
def train_models(X_train, y_train_keff, train_folder='VR1_DT_Lab_Training_Data'):
    # keff model
    keff_model = ensemble.RandomForestRegressor(n_estimators=100, random_state=42)
    keff_model.fit(X_train, y_train_keff)

    # Build snapshot matrix and SVD for flux ROM
    train_files = glob.glob(f'{train_folder}/results_case_*.npz')
    train_files.sort(key=lambda f: int(re.search(r'case_(\d+)', f).group(1)))
    S = []
    for f in train_files:
        flux = load_flux_data(f)
        S.append(flux.flatten())
    S = np.column_stack(S)
    U, Sigma, VT = np.linalg.svd(S, full_matrices=False)
    r = 11
    U_r = U[:, :r]
    C_train = np.dot(U_r.T, S)
    Y_train = C_train.T
    surrogate_model = ensemble.RandomForestRegressor(n_estimators=100, random_state=42)
    surrogate_model.fit(X_train, Y_train)
    return keff_model, surrogate_model, U_r

st.title('Digital Twin (Standalone widgets)')
st.write('This app recreates the k-eff and digital-twin widgets from the notebook.')

train_df, test_df, X_train, X_test, y_train_keff, y_test_keff = prepare_data()
keff_model, surrogate_model, U_r = train_models(X_train, y_train_keff)

st.sidebar.header('Input Parameters')
cr1 = st.sidebar.slider('CR 1 (cm)', 0.0, 84.7, 42.35, 0.1)
cr2 = st.sidebar.slider('CR 2 (cm)', 0.0, 84.7, 42.35, 0.1)
dummy_water = st.sidebar.slider('Dummy Water', 0.50, 1.00, 1.00, 0.01)
fa_water = st.sidebar.slider('FA Water', 0.50, 1.00, 1.00, 0.01)

st.header('K-effective widget')
input_state = np.array([[cr1, cr2, dummy_water, fa_water]])
pred_keff = keff_model.predict(input_state)[0]
st.write(f'Estimated k-effective: {pred_keff:.5f}')

# Show test-set performance
if st.checkbox('Show k-eff test performance'):
    preds = keff_model.predict(X_test)
    rmse = np.sqrt(mean_squared_error(y_test_keff, preds))
    mae = np.mean(np.abs(y_test_keff - preds))
    r2 = np.corrcoef(y_test_keff, preds)[0,1]**2
    st.write({'RMSE': float(rmse), 'MAE': float(mae), 'R2': float(r2)})
    fig, ax = plt.subplots()
    ax.scatter(y_test_keff, preds, alpha=0.7, color='purple')
    ax.plot([y_test_keff.min(), y_test_keff.max()],[y_test_keff.min(), y_test_keff.max()],'k--')
    ax.set_xlabel('True k-effective')
    ax.set_ylabel('Predicted k-effective')
    ax.set_title('K-effective: True vs Predicted')
    st.pyplot(fig)

st.header('Digital Twin: Predict flux from ROM')
z_index = st.slider('Z slice', 0, 69, 35)

# Predict modal coefficients and reconstruct
pred_coeffs = surrogate_model.predict(input_state).T
reconstructed_flat = np.dot(U_r, pred_coeffs).flatten()
reconstructed_3d = reconstructed_flat.reshape((NZ, NY, NX, NG))
therm_mid = reconstructed_3d[z_index, :, :, 0]

fig, ax = plt.subplots(figsize=(6,5))
ax.imshow(therm_mid, origin='lower', cmap='viridis')
ax.set_title(f'Reconstructed Thermal Flux (Z={z_index})')
st.pyplot(fig)

st.sidebar.markdown('---')
st.sidebar.write('Run this app with:')
st.sidebar.code('streamlit run digital_twin_files/rom/dt_lab_app.py')
