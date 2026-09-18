import io
from typing import Any
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

class PDFReportGenerator:
    def generate_pdf(self, report_data: dict[str, Any]) -> io.BytesIO:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=40,
            leftMargin=40,
            topMargin=40,
            bottomMargin=40
        )
        story = []
        styles = getSampleStyleSheet()

        # Custom Styles
        title_style = ParagraphStyle(
            "ReportTitle",
            parent=styles["Heading1"],
            fontSize=22,
            leading=26,
            textColor=colors.HexColor("#0f172a")
        )
        subtitle_style = ParagraphStyle(
            "ReportSubtitle",
            parent=styles["Normal"],
            fontSize=10,
            leading=14,
            textColor=colors.HexColor("#64748b")
        )
        section_heading = ParagraphStyle(
            "SectionHeading",
            parent=styles["Heading2"],
            fontSize=13,
            leading=18,
            textColor=colors.HexColor("#1e293b"),
            spaceBefore=12,
            spaceAfter=6
        )
        body_style = ParagraphStyle(
            "BodyText",
            parent=styles["Normal"],
            fontSize=9,
            leading=13,
            textColor=colors.HexColor("#334155")
        )
        badge_style = ParagraphStyle(
            "Badge",
            parent=styles["Normal"],
            fontSize=8,
            leading=10,
            textColor=colors.HexColor("#0284c7")
        )

        task = report_data.get("task", {})
        config = report_data.get("agent_config", {})
        scorecard = report_data.get("scorecard", {})
        dist = report_data.get("distributions", {})

        # 1. Header
        story.append(Paragraph("AgentBench Studio — Reliability Evaluation Report", title_style))
        story.append(Spacer(1, 4))
        meta_line = (
            f"<b>Batch ID:</b> {report_data.get('batch_id')} &nbsp;|&nbsp; "
            f"<b>Date:</b> {report_data.get('created_at', '')[:10]} &nbsp;|&nbsp; "
            f"<b>Evaluator Engine:</b> Multi-Metric v1.0"
        )
        story.append(Paragraph(meta_line, subtitle_style))
        story.append(Spacer(1, 10))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#cbd5e1"), spaceAfter=12))

        # 2. Benchmark Subject Meta
        meta_table_data = [
            [
                Paragraph(f"<b>Task:</b> {task.get('name')}", body_style),
                Paragraph(f"<b>Agent Config:</b> {config.get('name')}", body_style)
            ],
            [
                Paragraph(f"<b>Category:</b> {task.get('category')}", body_style),
                Paragraph(f"<b>Model:</b> {config.get('model')} ({config.get('provider')})", body_style)
            ],
            [
                Paragraph(f"<b>Total Iterations (N):</b> {scorecard.get('total_runs_count', 0)}", body_style),
                Paragraph(f"<b>Prompt Version:</b> {config.get('prompt_version')}", body_style)
            ]
        ]
        meta_table = Table(meta_table_data, colWidths=[260, 270])
        meta_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
            ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ]))
        story.append(meta_table)
        story.append(Spacer(1, 14))

        # 3. Summary Scorecard Table
        story.append(Paragraph("Quantitative Reliability Scorecard", section_heading))
        scorecard_data = [
            ["Metric", "Value", "Benchmark Target", "Status"],
            ["Overall Success Rate", f"{scorecard.get('overall_pass_rate', 0)}%", ">= 80.0%", "PASS" if scorecard.get('overall_pass_rate', 0) >= 80 else "FAIL"],
            ["Task Completion Rate", f"{scorecard.get('completion_rate', 0)}%", ">= 85.0%", "PASS" if scorecard.get('completion_rate', 0) >= 85 else "FAIL"],
            ["Tool-Call Accuracy", f"{scorecard.get('tool_call_accuracy', 0)}%", ">= 90.0%", "PASS" if scorecard.get('tool_call_accuracy', 0) >= 90 else "FAIL"],
            ["Citation Precision", f"{scorecard.get('citation_precision', 0)}%", ">= 80.0%", "PASS" if scorecard.get('citation_precision', 0) >= 80 else "FAIL"],
            ["Hallucination Rate", f"{scorecard.get('hallucination_rate', 0)}%", "<= 15.0%", "PASS" if scorecard.get('hallucination_rate', 0) <= 15 else "FAIL"],
            ["Avg Latency (ms)", f"{scorecard.get('avg_latency_ms', 0)} ms", "<= 10,000 ms", "PASS" if scorecard.get('avg_latency_ms', 0) <= 10000 else "FAIL"],
            ["Cost per Successful Task", f"${scorecard.get('cost_per_successful_task', 0):.5f}", "Efficiency Headline", "OPTIMAL"],
        ]
        sc_table = Table(scorecard_data, colWidths=[180, 110, 130, 110])
        sc_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f172a")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
            ("ALIGN", (1, 0), (-1, -1), "CENTER"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 9),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
        ]))
        story.append(sc_table)
        story.append(Spacer(1, 14))

        # 4. Statistical Distribution Across N Runs
        story.append(Paragraph("Distribution & Variance Statistics (N Runs)", section_heading))
        s_dist = dist.get("score", {})
        l_dist = dist.get("latency", {})
        c_dist = dist.get("cost", {})
        dist_data = [
            ["Dimension", "Min", "P25", "Median (P50)", "P75", "Max", "Std Dev"],
            ["Score (0-100)", str(s_dist.get("min")), str(s_dist.get("p25")), str(s_dist.get("p50")), str(s_dist.get("p75")), str(s_dist.get("max")), str(s_dist.get("std_dev"))],
            ["Latency (ms)", str(l_dist.get("min")), str(l_dist.get("p25")), str(l_dist.get("p50")), str(l_dist.get("p75")), str(l_dist.get("max")), str(l_dist.get("std_dev"))],
            ["Cost ($)", f"${c_dist.get('min', 0):.4f}", f"${c_dist.get('p25', 0):.4f}", f"${c_dist.get('p50', 0):.4f}", f"${c_dist.get('p75', 0):.4f}", f"${c_dist.get('max', 0):.4f}", f"${c_dist.get('std_dev', 0):.4f}"]
        ]
        d_table = Table(dist_data, colWidths=[120, 68, 68, 80, 68, 68, 60])
        d_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#334155")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        story.append(d_table)
        story.append(Spacer(1, 14))

        # 5. Worst-Run Forensic Drilldown
        worst_runs = report_data.get("worst_runs", [])
        if worst_runs:
            story.append(Paragraph("Worst-Run Forensic Drilldown", section_heading))
            for wr in worst_runs[:2]:
                fail_summary = "; ".join(wr.get("failure_reasons", [])) or "Met baseline requirements"
                wr_text = (
                    f"<b>Iteration #{wr.get('run_index')}</b> &nbsp;|&nbsp; "
                    f"Score: <b>{wr.get('overall_score')}/100</b> &nbsp;|&nbsp; "
                    f"Latency: {round(wr.get('latency_ms', 0), 1)}ms &nbsp;|&nbsp; "
                    f"Cost: ${wr.get('cost_usd', 0):.5f}<br/>"
                    f"<b>Evaluator Findings:</b> {fail_summary}"
                )
                story.append(Paragraph(wr_text, body_style))
                story.append(Spacer(1, 6))

        # Build document
        doc.build(story)
        buffer.seek(0)
        return buffer

pdf_generator = PDFReportGenerator()
