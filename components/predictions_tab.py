import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from utils.ml import ModelStudio

PALETTE = ["#5B4FF5", "#10B981", "#F59E0B", "#EF4444"]

def render_predictions():
    st.markdown("""
    <h2 style="font-family:'Space Grotesk',sans-serif;font-weight:600;margin-bottom:4px;">
        🔮 Future Predictions
    </h2>
    <p style="color:var(--muted,#6B7280);font-size:14px;margin-bottom:20px;">
        Forecast trends and predict future values using machine learning models.
    </p>
    """, unsafe_allow_html=True)

    if st.session_state.df is None:
        st.info("📂 Upload a dataset from the sidebar to enable predictions.")
        return

    df = st.session_state.df
    numeric_cols = df.select_dtypes(include="number").columns.tolist()

    if len(numeric_cols) < 2:
        st.warning("⚠️ Need at least 2 numeric columns for predictions.")
        return

    tab1, tab2 = st.tabs(["📈 Time-Series Forecast", "🎯 Predictive Studio Pro"])

    # --- Time Series Forecast (Kept original logic but polished) ---
    with tab1:
        st.markdown("**Empower your decisions with trend extrapolation.**")

        col1, col2 = st.columns(2)
        with col1:
            target_col = st.selectbox("Column to Forecast", numeric_cols, key="ts_target")
        with col2:
            forecast_steps = st.slider("Forecast Steps (periods ahead)", 5, 100, 20, key="ts_steps")

        if st.button("🔮 Run Forecast", key="ts_run", use_container_width=True):
            with st.spinner("Analyzing historical trends..."):
                try:
                    from sklearn.linear_model import LinearRegression
                    from sklearn.preprocessing import PolynomialFeatures
                    from sklearn.pipeline import Pipeline

                    series = df[target_col].dropna().reset_index(drop=True)
                    X = np.arange(len(series)).reshape(-1, 1)
                    y = series.values

                    model = Pipeline([
                        ("poly", PolynomialFeatures(degree=2)),
                        ("reg", LinearRegression())
                    ])
                    model.fit(X, y)

                    X_future = np.arange(len(series) + forecast_steps).reshape(-1, 1)
                    y_pred = model.predict(X_future)
                    residuals = y - model.predict(X).flatten()
                    std = residuals.std()

                    fig = go.Figure()
                    fig.add_trace(go.Scatter(x=list(range(len(series))), y=series.values, mode="lines", name="Historical", line=dict(color=PALETTE[0])))
                    
                    future_x = list(range(len(series), len(series) + forecast_steps))
                    future_y = y_pred[len(series):]
                    fig.add_trace(go.Scatter(x=future_x, y=future_y, mode="lines+markers", name="Forecast", line=dict(color=PALETTE[1], dash="dash")))

                    fig.update_layout(template="simple_white", height=400, margin=dict(l=0,r=0,t=20,b=0))
                    st.plotly_chart(fig, use_container_width=True)
                except Exception as e:
                    st.error(f"Forecast error: {e}")

    # --- Predictive Studio Pro (THE NEW OVERHAUL) ---
    with tab2:
        st.markdown("### 🧪 The Modeling Lab")
        st.info("Comparing multiple algorithms to find the most accurate predictor for your data.")

        # Configuration
        with st.expander("🛠️ Advanced Model Settings", expanded=False):
            c1, c2 = st.columns(2)
            with c1:
                test_size = st.slider("Test Data Split (%)", 10, 50, 20) / 100
            with c2:
                n_trees = st.number_input("Tree Count (RF/GB)", 10, 1000, 100)

        col1, col2 = st.columns([1, 2])
        with col1:
            target = st.selectbox("Target (What to predict?)", numeric_cols, key="studio_target")
            all_features = [c for c in numeric_cols if c != target]
            features = st.multiselect("Features (Influencing factors)", all_features, default=all_features[:3], key="studio_features")
        
        with col2:
            st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
            run_btn = st.button("🚀 Train Studio Leaderboard", type="primary", use_container_width=True)

        if run_btn and features:
            studio = ModelStudio(df, target, features, test_size=test_size)
            with st.spinner("Running Multi-Model Comparison..."):
                results = studio.train_all(params={
                    "Random Forest": {"n_estimators": n_trees},
                    "Gradient Boosting": {"n_estimators": n_trees}
                })
                st.session_state["ml_studio"] = studio
                st.session_state["ml_results"] = results
            
        if "ml_results" in st.session_state:
            results = st.session_state["ml_results"]
            studio = st.session_state["ml_studio"]

            # Leaderboard Table
            st.markdown("#### 🏆 Algorithm Leaderboard")
            res_df = pd.DataFrame(results).T.reset_index().rename(columns={"index": "Model"})
            res_df = res_df.sort_values("R2", ascending=False)
            
            # Highlight winner
            winner = res_df.iloc[0]["Model"]
            
            # Custom display for leaderboard
            cols = st.columns(len(res_df))
            for i, row in res_df.iterrows():
                with cols[i % 4]:
                    is_winner = row['Model'] == winner
                    border_color = PALETTE[1] if is_winner else "var(--border)"
                    st.markdown(f"""
                    <div style="border:1px solid {border_color}; padding:15px; border-radius:12px; background:rgba(255,255,255,0.05); text-align:center;">
                        <div style="font-size:10px; opacity:0.6; text-transform:uppercase;">{row['Model']}</div>
                        <div style="font-size:24px; font-weight:700; color:{PALETTE[1] if is_winner else PALETTE[0]}">{row['R2']:.3f}</div>
                        <div style="font-size:11px; opacity:0.8;">Accuracy (R²)</div>
                        {f'<div class="badge badge-green" style="margin-top:8px">⭐ BEST</div>' if is_winner else ''}
                    </div>
                    """, unsafe_allow_html=True)

            st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)

            # Interactive Playground
            st.markdown("#### 🎮 Prediction Playground")
            st.write("Enter custom values below to see the model's prediction in real-time.")
            
            play_c1, play_c2 = st.columns([1, 1])
            input_values = {}
            
            with play_c1:
                st.markdown("<div style='padding:15px; border:1px solid var(--border); border-radius:12px;'>", unsafe_allow_html=True)
                for f in features:
                    f_min = float(df[f].min())
                    f_max = float(df[f].max())
                    f_mean = float(df[f].mean())
                    input_values[f] = st.slider(f"Adjust {f}", f_min, f_max, f_mean)
                st.markdown("</div>", unsafe_allow_html=True)

            with play_c2:
                selected_model_name = st.selectbox("Predict using model:", list(studio.trained_models.keys()))
                model = studio.trained_models[selected_model_name]
                
                # Predict
                input_df = pd.DataFrame([input_values])
                
                # Scale if linear
                if "Regression" in selected_model_name:
                    input_arr = studio.scaler.transform(input_df)
                else:
                    input_arr = input_df.values
                
                prediction = model.predict(input_arr)[0]
                
                st.markdown(f"""
                <div style="background:{PALETTE[0]}; color:white; padding:30px; border-radius:12px; text-align:center; box-shadow:0 10px 30px rgba(91, 79, 245, 0.3);">
                    <div style="font-size:14px; opacity:0.9;">Predicted {target}</div>
                    <div style="font-size:48px; font-weight:800; margin:10px 0;">{prediction:,.2f}</div>
                    <div style="font-size:12px; opacity:0.7;">Based on {selected_model_name}</div>
                </div>
                """, unsafe_allow_html=True)
                
                # Code Export
                st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
                code = studio.generate_python_code(selected_model_name)
                st.download_button(
                    label=f"💾 Download {selected_model_name} Script",
                    data=code,
                    file_name=f"{selected_model_name.lower().replace(' ', '_')}_model.py",
                    mime="text/x-python",
                    use_container_width=True
                )
