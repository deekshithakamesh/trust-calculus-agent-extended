"""
trustcalc.analysis
==================

Analysis package for the Trust Calculus framework.

Provides:

- Attack result analysis
- Leakage analysis
- Statistical summaries
- Evaluation metrics
- Plot generation
- Visualization management
- Report generation
"""

from .analyzer import (
    Analyzer,
    AnalysisResult,
)

from .leakage import (
    LeakageAnalyzer,
    LeakageMetrics,
)

from .statistics import (
    StatisticsAnalyzer,
    StatisticsSummary,
)

from .metrics import (
    MetricsAnalyzer,
    EvaluationMetrics,
)

from .plots import (
    PlotGenerator,
)

from .visualization import (
    VisualizationManager,
)

from .report import (
    Report,
    ReportGenerator,
)

__all__ = [
    # Analyzer
    "Analyzer",
    "AnalysisResult",

    # Leakage
    "LeakageAnalyzer",
    "LeakageMetrics",

    # Statistics
    "StatisticsAnalyzer",
    "StatisticsSummary",

    # Metrics
    "MetricsAnalyzer",
    "EvaluationMetrics",

    # Plots
    "PlotGenerator",

    # Visualization
    "VisualizationManager",

    # Reports
    "Report",
    "ReportGenerator",
]