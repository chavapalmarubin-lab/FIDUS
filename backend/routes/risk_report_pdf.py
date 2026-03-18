"""
FIDUS Risk Compliance Report — PDF Generator
Generates professional PDF reports per manager for distribution.
"""

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone
from io import BytesIO
import os
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/admin/risk", tags=["Risk Report PDF"])

MONGO_URL = os.environ.get("MONGO_URL")

INITIAL_ALLOCATIONS = {2206: 179316.36, 20043: 178000.00, 2208: 50000.00}

SIZING_RULES = [
    ("GOLD (XAUUSD)", "0.10 – 0.30", "HIGH", "3", "0.60 x ATR(14)", "$10"),
    ("FOREX Majors", "0.50 – 1.00", "MEDIUM", "5–7", "0.75 x ATR(14)", "20 pips"),
    ("FOREX Crosses", "0.30 – 0.70", "MEDIUM", "4–5", "1.00 x ATR(14)", "30 pips"),
    ("INDICES (US30, DE40)", "1.0 – 3.0", "MED-HIGH", "3–5", "0.80 x ATR(14)", "50 pts"),
    ("OIL (USOIL)", "0.10 – 0.30", "HIGH", "3", "0.70 x ATR(14)", "$0.50"),
    ("BTC (Bitcoin)", "0.10 – 0.30", "HIGH", "2–3", "0.50 x ATR(14)", "$500"),
    ("ETH (Ethereum)", "0.20 – 0.50", "MED-HIGH", "3", "0.55 x ATR(14)", "$30"),
]

RISK_PARAMS = [
    ("Max Risk Per Trade", "0.25% – 0.75%"),
    ("Max Intraday Drawdown", "5% (hard stop)"),
    ("Max Weekly Loss", "6%"),
    ("Max Monthly Drawdown", "10%"),
    ("Max Margin Usage", "25%"),
    ("Leverage", "200:1"),
    ("Force Flat Time", "21:50 UTC (16:50 NY)"),
    ("Overnight Positions", "PROHIBITED"),
    ("Max Single Instrument", "10x equity"),
    ("Max Total Notional", "20x equity"),
]


@router.get("/report/pdf/{account_id}")
async def generate_risk_report_pdf(account_id: int):
    """Generate a PDF risk compliance report for a manager/account."""
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.units import inch
        from reportlab.lib.colors import HexColor, white, black
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT

        client = AsyncIOMotorClient(MONGO_URL)
        db = client.fidus_production

        acc = await db.mt5_accounts.find_one({"account": account_id}, {"_id": 0})
        if not acc:
            raise HTTPException(status_code=404, detail=f"Account {account_id} not found")

        manager_name = acc.get("manager_name", f"Account {account_id}")
        equity = acc.get("equity", 0) or 0
        balance = acc.get("balance", 0) or 0
        initial = acc.get("initial_allocation", 0) or INITIAL_ALLOCATIONS.get(account_id, 0)

        # Get trade stats
        pipeline = [
            {"$match": {"account": account_id, "type": {"$ne": 2}, "profit": {"$ne": 0}}},
            {"$group": {
                "_id": None,
                "total_trades": {"$sum": 1},
                "wins": {"$sum": {"$cond": [{"$gt": ["$profit", 0]}, 1, 0]}},
                "losses": {"$sum": {"$cond": [{"$lt": ["$profit", 0]}, 1, 0]}},
                "total_profit": {"$sum": {"$cond": [{"$gt": ["$profit", 0]}, "$profit", 0]}},
                "total_loss": {"$sum": {"$cond": [{"$lt": ["$profit", 0]}, "$profit", 0]}},
            }}
        ]
        stats_result = list(await db.mt5_deals_history.aggregate(pipeline).to_list(1))
        stats = stats_result[0] if stats_result else {}

        total_trades = stats.get("total_trades", 0)
        wins = stats.get("wins", 0)
        win_rate = (wins / total_trades * 100) if total_trades > 0 else 0
        profit_factor = abs(stats.get("total_profit", 0) / stats.get("total_loss", 1)) if stats.get("total_loss", 0) != 0 else 0
        dd_pct = ((equity - initial) / initial * 100) if initial > 0 else 0

        now = datetime.now(timezone.utc)
        client.close()

        # ── Build PDF ──
        buf = BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=letter, topMargin=0.6*inch, bottomMargin=0.5*inch, leftMargin=0.7*inch, rightMargin=0.7*inch)

        styles = getSampleStyleSheet()
        navy = HexColor("#0a1628")
        cyan = HexColor("#0ea5e9")
        red = HexColor("#ef4444")
        green = HexColor("#10b981")
        amber = HexColor("#f59e0b")
        purple = HexColor("#8b5cf6")
        slate = HexColor("#64748b")
        dark = HexColor("#1e293b")
        light = HexColor("#cbd5e1")

        title_style = ParagraphStyle("Title", parent=styles["Title"], fontSize=22, textColor=cyan, spaceAfter=2, fontName="Helvetica-Bold")
        subtitle_style = ParagraphStyle("Sub", parent=styles["Normal"], fontSize=10, textColor=slate, spaceAfter=12)
        heading_style = ParagraphStyle("H2", parent=styles["Heading2"], fontSize=14, textColor=cyan, spaceBefore=16, spaceAfter=6, fontName="Helvetica-Bold")
        red_heading = ParagraphStyle("H2R", parent=heading_style, textColor=red)
        purple_heading = ParagraphStyle("H2P", parent=heading_style, textColor=purple)
        body_style = ParagraphStyle("Body", parent=styles["Normal"], fontSize=10, textColor=HexColor("#334155"), leading=14)
        small_style = ParagraphStyle("Small", parent=styles["Normal"], fontSize=8, textColor=slate, leading=10)
        mono_style = ParagraphStyle("Mono", parent=styles["Normal"], fontSize=9, textColor=green, fontName="Courier", leading=12, backColor=HexColor("#f0f4f8"), borderPadding=8)

        elements = []

        # Header
        elements.append(Paragraph("FIDUS INVESTMENT MANAGEMENT", ParagraphStyle("FH", parent=styles["Normal"], fontSize=10, textColor=slate, spaceAfter=2)))
        elements.append(Paragraph(f"Risk Compliance Report", title_style))
        elements.append(Paragraph(f"{manager_name} — Account #{account_id}", subtitle_style))
        elements.append(Paragraph(f"Generated: {now.strftime('%B %d, %Y at %H:%M UTC')} | CONFIDENTIAL", small_style))
        elements.append(HRFlowable(width="100%", thickness=1, color=cyan, spaceAfter=12))

        # KPI Summary
        elements.append(Paragraph("Account Summary", heading_style))
        kpi_data = [
            ["Equity", "Initial Allocation", "TRUE P&L", "Drawdown", "Trades", "Win Rate", "Profit Factor"],
            [f"${equity:,.2f}", f"${initial:,.2f}", f"${equity-initial:+,.2f}", f"{dd_pct:+.2f}%", str(total_trades), f"{win_rate:.1f}%", f"{profit_factor:.2f}"],
        ]
        kpi_table = Table(kpi_data, colWidths=[95, 95, 85, 70, 50, 60, 70])
        kpi_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), dark),
            ("TEXTCOLOR", (0, 0), (-1, 0), light),
            ("FONTSIZE", (0, 0), (-1, 0), 8),
            ("FONTSIZE", (0, 1), (-1, 1), 10),
            ("FONTNAME", (0, 1), (-1, 1), "Helvetica-Bold"),
            ("TEXTCOLOR", (0, 1), (-1, 1), HexColor("#1a1a2e")),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#e2e8f0")),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ]))
        elements.append(kpi_table)
        elements.append(Spacer(1, 8))

        # Compliance Checklist
        elements.append(Paragraph("Compliance Checklist", heading_style))
        checks = [
            ("Max Drawdown <= 10%", f"{dd_pct:.2f}%", "FAIL" if dd_pct < -10 else "WARN" if dd_pct < -5 else "PASS"),
            ("Win Rate >= 30%", f"{win_rate:.1f}%", "PASS" if win_rate >= 30 else "FAIL"),
            ("Profit Factor >= 1.0", f"{profit_factor:.2f}", "PASS" if profit_factor >= 1.5 else "WARN" if profit_factor >= 1.0 else "FAIL"),
        ]
        check_data = [["Requirement", "Actual Value", "Status"]]
        for check, actual, sev in checks:
            check_data.append([check, actual, sev])

        check_table = Table(check_data, colWidths=[250, 120, 80])
        sev_colors = {"PASS": green, "WARN": amber, "FAIL": red}
        styles_list = [
            ("BACKGROUND", (0, 0), (-1, 0), dark),
            ("TEXTCOLOR", (0, 0), (-1, 0), light),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("ALIGN", (1, 0), (-1, -1), "CENTER"),
            ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#e2e8f0")),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ]
        for i, (_, _, sev) in enumerate(checks, 1):
            styles_list.append(("TEXTCOLOR", (2, i), (2, i), sev_colors.get(sev, black)))
            styles_list.append(("FONTNAME", (2, i), (2, i), "Helvetica-Bold"))
        check_table.setStyle(TableStyle(styles_list))
        elements.append(check_table)
        elements.append(Spacer(1, 8))

        # FIDUS Risk Parameters
        elements.append(Paragraph("FIDUS Risk Parameters — MANDATORY", red_heading))
        elements.append(Paragraph("All money managers and trading algorithms MUST comply with these limits. Non-compliance triggers alerts, review, and potential suspension.", body_style))
        elements.append(Spacer(1, 4))

        param_data = [["Parameter", "Required Value"]]
        for p, v in RISK_PARAMS:
            param_data.append([p, v])

        param_table = Table(param_data, colWidths=[300, 150])
        param_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), red),
            ("TEXTCOLOR", (0, 0), (-1, 0), white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("ALIGN", (1, 0), (1, -1), "RIGHT"),
            ("FONTNAME", (1, 1), (1, -1), "Courier-Bold"),
            ("TEXTCOLOR", (1, 1), (1, -1), HexColor("#991b1b")),
            ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#fecaca")),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [HexColor("#fff7f7"), white]),
        ]))
        elements.append(param_table)
        elements.append(Spacer(1, 8))

        # Position Sizing
        elements.append(Paragraph("Position Sizing — Institutional Model", heading_style))
        elements.append(Paragraph("Position Size = (Equity x Risk per Trade) / (ATR x Volatility Multiplier)", body_style))
        elements.append(Spacer(1, 4))

        sizing_data = [["Asset Class", "Lots per $100K", "Risk Level", "Max Trades", "ATR Stop", "Default Stop"]]
        for row in SIZING_RULES:
            sizing_data.append(list(row))

        sizing_table = Table(sizing_data, colWidths=[110, 80, 70, 60, 80, 60])
        sizing_styles = [
            ("BACKGROUND", (0, 0), (-1, 0), cyan),
            ("TEXTCOLOR", (0, 0), (-1, 0), white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("FONTNAME", (1, 1), (1, -1), "Courier-Bold"),
            ("TEXTCOLOR", (1, 1), (1, -1), cyan),
            ("ALIGN", (1, 0), (-1, -1), "CENTER"),
            ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#e2e8f0")),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [HexColor("#f0f9ff"), white]),
        ]
        for i, row in enumerate(SIZING_RULES, 1):
            risk = row[2]
            color = red if "HIGH" in risk else amber if "MED" in risk else green
            sizing_styles.append(("TEXTCOLOR", (2, i), (2, i), color))
            sizing_styles.append(("FONTNAME", (2, i), (2, i), "Helvetica-Bold"))
        sizing_table.setStyle(TableStyle(sizing_styles))
        elements.append(sizing_table)
        elements.append(Spacer(1, 8))

        # Algorithm Config
        elements.append(Paragraph("Algorithm Configuration", purple_heading))
        elements.append(Paragraph("Configure your trading system with these parameters:", body_style))
        elements.append(Spacer(1, 4))

        config_text = f"""# FIDUS RISK CONFIG — {manager_name} (#{account_id})
# {now.strftime('%Y-%m-%d')}

[DRAWDOWN]  max_intraday=5%  max_weekly=6%  max_monthly=10%
[SIZING]    risk_per_trade=0.50%  max_margin=25%
[HOURS]     force_flat=21:50UTC  overnight=PROHIBITED
[GOLD]      max_lots=0.30  max_trades=3  stop=0.60xATR
[FOREX]     max_lots=1.00  max_trades=7  stop=0.75xATR
[INDEX]     max_lots=3.00  max_trades=5  stop=0.80xATR"""

        elements.append(Paragraph(config_text.replace("\n", "<br/>"), mono_style))
        elements.append(Spacer(1, 16))

        # Footer
        elements.append(HRFlowable(width="100%", thickness=0.5, color=slate, spaceAfter=4))
        elements.append(Paragraph(f"FIDUS Investment Management | Risk Compliance Report | {manager_name} (#{account_id}) | {now.strftime('%Y-%m-%d')}", small_style))
        elements.append(Paragraph("CONFIDENTIAL — This document contains proprietary risk parameters. Do not distribute without authorization.", small_style))

        doc.build(elements)
        buf.seek(0)

        filename = f"FIDUS_Risk_Report_{manager_name.replace(' ', '_')}_{account_id}_{now.strftime('%Y%m%d')}.pdf"

        return StreamingResponse(
            buf,
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'}
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"PDF generation error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
