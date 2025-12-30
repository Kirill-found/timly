import re

# Read the file
with open('src/pages/Analysis.tsx', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace the old useEffect with the new one
old_pattern = r'''  useEffect\(\(\) => \{
    if \(!app\.activeAnalysis\) return;
    const pollStats = async \(\) => \{
      try \{
        const stats = await apiClient\.getApplicationsStats\(app\.activeAnalysis!\.vacancyId\);
        app\.updateAnalysisProgress\(\{ analyzed: stats\.analyzed_applications \}\);
        if \(stats\.unanalyzed_applications === 0 \|\| stats\.analyzed_applications >= app\.activeAnalysis!\.total\) \{
          app\.stopAnalysis\(\);
          loadResults\(\);
          loadApplicationsStats\(\);
          loadDashboardStats\(\);
          loadLimits\(\);
        \}
      \} catch \(err\) \{
        console\.error\('\[Analysis\] Polling error:', err\);
      \}
    \};
    app\.startGlobalPolling\(pollStats, 3000, 300000\);
  \}, \[app\.activeAnalysis\?\.vacancyId\]\);'''

new_code = '''  useEffect(() => {
    if (!app.activeAnalysis) {
      initialAnalyzedRef.current = null;
      return;
    }

    const pollStats = async () => {
      try {
        const stats = await apiClient.getApplicationsStats(app.activeAnalysis!.vacancyId);

        // При первом запросе запоминаем начальное значение
        if (initialAnalyzedRef.current === null) {
          initialAnalyzedRef.current = stats.analyzed_applications;
        }

        // Вычисляем прогресс относительно начала текущей сессии
        const newlyAnalyzed = stats.analyzed_applications - initialAnalyzedRef.current;
        app.updateAnalysisProgress({ analyzed: Math.max(0, newlyAnalyzed) });

        // Проверяем завершение
        if (stats.unanalyzed_applications === 0 || newlyAnalyzed >= app.activeAnalysis!.total) {
          app.stopAnalysis();
          loadResults();
          loadApplicationsStats();
          loadDashboardStats();
          loadLimits();
        }
      } catch (err) {
        console.error('[Analysis] Polling error:', err);
      }
    };
    app.startGlobalPolling(pollStats, 3000, 300000);
  }, [app.activeAnalysis?.vacancyId]);'''

# Simple string replace
old_str = '''  useEffect(() => {
    if (!app.activeAnalysis) return;
    const pollStats = async () => {
      try {
        const stats = await apiClient.getApplicationsStats(app.activeAnalysis!.vacancyId);
        app.updateAnalysisProgress({ analyzed: stats.analyzed_applications });
        if (stats.unanalyzed_applications === 0 || stats.analyzed_applications >= app.activeAnalysis!.total) {
          app.stopAnalysis();
          loadResults();
          loadApplicationsStats();
          loadDashboardStats();
          loadLimits();
        }
      } catch (err) {
        console.error('[Analysis] Polling error:', err);
      }
    };
    app.startGlobalPolling(pollStats, 3000, 300000);
  }, [app.activeAnalysis?.vacancyId]);'''

if old_str in content:
    content = content.replace(old_str, new_code)
    print("Replaced polling useEffect")
else:
    print("Pattern not found")

# Write back
with open('src/pages/Analysis.tsx', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done!")
