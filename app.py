import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import io

# --- 绘图核心函数 ---
def create_prism_style_plot(df, replicate_cols):
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
st.write("导入任意格式的 Excel 表格，自由配置数据列，一键生成类似 GraphPad Prism 风格的科学图表。")

uploaded_file = st.file_uploader("📂 请选择并上传您的 Excel 结果文件", type="xlsx")

if uploaded_file is not None:
    st.success("✅ 文件上传成功！")
    dataframe = pd.read_excel(uploaded_file)
    
    st.subheader("📊 数据预览 (前 5 行)")
    st.dataframe(dataframe.head())
    
    # 获取 Excel 文件的所有列名
    all_columns = list(dataframe.columns)
    
    # 1. 智能猜测重复孔列
    default_replicates = [
        col for col in all_columns 
        if any(keyword in str(col).lower() for keyword in ['replicate', 'rep', '孔', '平行', 'r1', 'r2', 'r3', 'dup', 'parallel'])
    ]
    
    st.subheader("⚙️ 属性匹配设置（请确认是否正确）")
    
    # 2. 选择抗体列
    default_ab_col = "Antibody Name" if "Antibody Name" in all_columns else (all_columns[0] if len(all_columns) > 0 else "")
    ab_col = st.selectbox("1. 选择【抗体名称】所在列：", all_columns, index=all_columns.index(default_ab_col) if default_ab_col in all_columns else 0)
    
    # 3. 选择浓度列
    default_conc_col = "Concentration (nM)" if "Concentration (nM)" in all_columns else (all_columns[1] if len(all_columns) > 1 else all_columns[0])
    conc_col = st.selectbox("2. 选择【浓度】所在列：", all_columns, index=all_columns.index(default_conc_col) if default_conc_col in all_columns else 0)
    
    # 4. 选择重复孔列
    selected_replicates = st.multiselect(
        "3. 选择所有包含【重复孔数据】的列（可多选，系统已为您自动勾选推荐列）：", 
        options=all_columns, 
        default=default_replicates
    )
    
    # 拷贝并重命名数据列，使其适配绘图函数
    plot_df = dataframe.copy()
    plot_df = plot_df.rename(columns={ab_col: 'Antibody Name', conc_col: 'Concentration (nM)'})
    
    if len(selected_replicates) < 1:
        st.warning("⚠️ 请在上方第 3 步中，至少选择一列作为重复孔数据！")
    else:
        st.subheader("📈 Prism 风格剂量效应曲线")
        fig = create_prism_style_plot(plot_df, selected_replicates)
        
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
