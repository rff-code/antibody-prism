import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import io

# --- 绘图核心函数 ---
def create_prism_style_plot(df):
    replicate_cols = [col for col in df.columns if 'Replicate' in str(col)]
    if not replicate_cols:
        st.error("❌ 未在 Excel 中找到包含 'Replicate' 关键字的重复孔数据列！")
        return None

    # 计算均值和标准差 (SD)
    df['Mean'] = df[replicate_cols].mean(axis=1)
    df['StdDev'] = df[replicate_cols].std(axis=1)

    # 绘图设置 (GraphPad Prism 经典风格)
    fig, ax = plt.subplots(figsize=(8, 6))
    antibodies = df['Antibody Name'].unique()
    
    # 颜色调配
    colors = plt.cm.get_cmap('Set1')(np.linspace(0, 1, len(antibodies)))

    for i, ab in enumerate(antibodies):
        ab_data = df[df['Antibody Name'] == ab].sort_values('Concentration (nM)')
        
        # 绘制带误差棒的数据点和折线
        ax.errorbar(
            ab_data['Concentration (nM)'], 
            ab_data['Mean'], 
            yerr=ab_data['StdDev'],
            fmt='-o',          # 实心圆点连接折线
            capsize=5,         # 误差棒横条大小
            label=ab, 
            color=colors[i], 
            markersize=6, 
            linewidth=2
        )

    # Prism 样式精细化调整
    ax.set_xscale('log') # X 轴半对数刻度
    ax.set_xlabel('Concentration (nM)', fontsize=14, fontweight='bold')
    ax.set_ylabel('Reporter Signal (RLU)', fontsize=14, fontweight='bold')
    ax.set_title('Antibody Screening Dose-Response', fontsize=16, fontweight='bold')
    
    # 刻度线朝外，加粗边框
    ax.tick_params(axis='both', which='major', labelsize=12, direction='out', length=6, width=1.5)
    ax.grid(True, which='both', linestyle='--', linewidth=0.5, alpha=0.5)
    
    for spine in ['top', 'right', 'left', 'bottom']:
        ax.spines[spine].set_linewidth(1.5)
        
    ax.legend(title='Antibody', fontsize=12, frameon=True)
    fig.tight_layout()
    return fig

# --- Streamlit 网页布局 ---
st.set_page_config(page_title="抗体筛选数据可视化", layout="centered")
st.title('🔬 抗体筛选数据在线作图工具')
st.write("导入包含多孔重复数据的 Excel 表格，一键生成类似 GraphPad Prism 风格的科学图表。")

uploaded_file = st.file_uploader("📂 请选择并上传您的 Excel 结果文件", type="xlsx")

if uploaded_file is not None:
    st.success("✅ 文件上传成功！")
    dataframe = pd.read_excel(uploaded_file)
    
    st.subheader("📊 数据预览 (前 5 行)")
    st.dataframe(dataframe.head())
    
    st.subheader("📈 Prism 风格剂量效应曲线")
    fig = create_prism_style_plot(dataframe)
    
    if fig is not None:
        st.pyplot(fig)
        
        # 内存缓冲导出 PNG 图片
        buf = io.BytesIO()
        fig.savefig(buf, format="png", dpi=300)
        
        st.download_button(
            label="💾 下载高清图表 (PNG)",
            data=buf.getvalue(),
            file_name="antibody_dose_response.png",
            mime="image/png"
        )
