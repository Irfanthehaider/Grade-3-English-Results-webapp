from flask import Flask, render_template
import pandas as pd
import plotly.graph_objects as go

app = Flask(__name__)

SUBJECTS = [
    'Vocabulary and Usage', 'Functional Grammar', 'Textual Activities',
    'Writing Skills', 'Internal Evaluation', 'External Evaluation',
    'Pronunciation of Words', 'Paragraph Reading', 'Script Listening', 'Dictation'
]

SECTIONS = {
    'Pink':   'data/English_Boys_Pink.xlsx',
    'White':  'data/English_Boys_White.xlsx',
    'Yellow': 'data/English_Boys_Yellow.xlsx',
}

def get_grade(pct):
    if pct >= 90: return 'A+'
    elif pct >= 80: return 'A'
    elif pct >= 70: return 'B'
    elif pct >= 60: return 'C'
    elif pct >= 50: return 'D'
    else: return 'F'

def load_section(filepath, section_name):
    df = pd.read_excel(filepath, sheet_name='Sheet1', header=0)
    df.columns = ['teacher_id', 'Roll No.', 'Student Name'] + SUBJECTS
    df = df.dropna(subset=['Student Name'])
    for subj in SUBJECTS:
        df[subj] = pd.to_numeric(df[subj], errors='coerce').fillna(0)
    df['Total'] = df[SUBJECTS].sum(axis=1)
    df['Percentage'] = (df['Total'] / 145 * 100).round(2)
    df['Grade'] = df['Percentage'].apply(get_grade)  
    df['Section'] = section_name
    return df

def load_all():
    frames = [load_section(path, name) for name, path in SECTIONS.items()]
    return pd.concat(frames, ignore_index=True)


@app.route('/')
def home():
    all_df = load_all()

    section_stats = {}
    for sec in SECTIONS:
        df = all_df[all_df['Section'] == sec]
        section_stats[sec] = {
            'count':   len(df),
            'average': round(df['Percentage'].mean(), 2),
            'highest': round(df['Total'].max(), 2),
        }

    # Build chart in Python
    fig = go.Figure(data=[
        go.Bar(
            x=list(section_stats.keys()),
            y=[s['average'] for s in section_stats.values()],
            marker_color=['#e91e8c', '#6c757d', '#f5a623'],
            marker_line_width=0,
            text=[f"{s['average']}%" for s in section_stats.values()],
            textposition='outside'
        )
    ])

    fig.update_layout(
        yaxis=dict(range=[0, 100], title='Average %'),
        xaxis_title='Section',
        plot_bgcolor='white',
        paper_bgcolor='white',
        margin=dict(t=20, b=40, l=40, r=20),
        height=320
    )

    # Convert to HTML snippet — no CDN needed
    section_chart = fig.to_html(full_html=False, include_plotlyjs='cdn')

    return render_template('index.html',
        section_stats=section_stats,
        section_chart=section_chart
    )

@app.route('/section/<name>')
def section_view(name):
    if name not in SECTIONS:
        return "Section not found", 404

    df = load_section(SECTIONS[name], name)
    df = df.sort_values('Total', ascending=False).reset_index(drop=True)

    students = df[['Roll No.', 'Student Name', 'Total', 'Percentage', 'Grade']].to_dict(orient='records')
    avg = round(df['Percentage'].mean(), 2)

    grade_counts = df['Grade'].value_counts()

    grade_colors = {
        'A+': '#28a745', 'A': '#007bff', 'B': '#6f42c1',
        'C':  '#ffc107', 'D': '#fd7e14', 'F': '#dc3545'
    }

    fig = go.Figure(data=[
        go.Pie(
            labels=grade_counts.index.tolist(),
            values=grade_counts.values.tolist(),
            marker_colors=[grade_colors.get(g, '#ccc') for g in grade_counts.index],
            hole=0.4,          # makes it a doughnut
            textinfo='label+percent'
        )
    ])

    fig.update_layout(
        showlegend=True,
        legend=dict(orientation='v', x=1, y=0.5),
        margin=dict(t=20, b=20, l=20, r=20),
        height=300,
        paper_bgcolor='white'
    )

    grade_chart = fig.to_html(full_html=False, include_plotlyjs='cdn')

    return render_template('section.html',
        section=name,
        students=students,
        avg=avg,
        grade_chart=grade_chart
    )
@app.route('/student/<roll>')
def student_view(roll):
    all_df = load_all()
    row = all_df[all_df['Roll No.'] == roll]

    if row.empty:
        return "Student not found", 404

    student = row.iloc[0].to_dict()

    subject_scores = [
        {'subject': subj, 'score': student[subj]}
        for subj in SUBJECTS
    ]

    sec_df = all_df[all_df['Section'] == student['Section']].copy()
    sec_df = sec_df.sort_values('Total', ascending=False).reset_index(drop=True)
    rank = sec_df[sec_df['Roll No.'] == roll].index[0] + 1

    # Short subject names for axis labels
    short_subjects = [s.split()[0] + ' ' + s.split()[1] if len(s.split()) > 1 else s
                      for s in SUBJECTS]

    scores = [student[s] for s in SUBJECTS]

    fig = go.Figure(data=[
        go.Bar(
            x=short_subjects,
            y=scores,
            marker_color='#4c9be8',
            marker_line_width=0,
            text=scores,
            textposition='outside'
        )
    ])

    fig.update_layout(
        yaxis=dict(title='Score', rangemode='tozero'),
        xaxis=dict(tickangle=-30),
        plot_bgcolor='white',
        paper_bgcolor='white',
        margin=dict(t=20, b=80, l=40, r=20),
        height=340
    )

    student_chart = fig.to_html(full_html=False, include_plotlyjs='cdn')

    return render_template('student.html',
        student=student,
        subject_scores=subject_scores,
        rank=rank,
        section_count=len(sec_df),
        student_chart=student_chart
    )
if __name__ == '__main__':
    app.run(debug=True)