import re

# Read the file
with open('src/components/Layout/AppLayout.tsx', 'r', encoding='utf-8') as f:
    content = f.read()

old_str = '''            <div className="flex items-center gap-3 mb-3">
              <div className="relative">
                <Brain className="w-5 h-5 text-zinc-400" />
                <Loader2 className="w-3 h-3 text-zinc-400 animate-spin absolute -top-1 -right-1" />
              </div>
              <div className="flex-1 min-w-0">
                <div className="text-sm font-medium text-zinc-200">Анализ резюме</div>
                <div className="text-xs text-zinc-500">
                  {activeAnalysis.analyzed} из {activeAnalysis.total}
                </div>
              </div>'''

new_str = '''            <div className="flex items-center gap-3 mb-3">
              <div className="w-8 h-8 rounded-lg bg-zinc-800 flex items-center justify-center">
                <Loader2 className="w-4 h-4 text-zinc-400 animate-spin" />
              </div>
              <div className="flex-1 min-w-0">
                <div className="text-sm font-medium text-zinc-200">Анализ</div>
                <div className="text-xs text-zinc-500">
                  {activeAnalysis.analyzed} / {activeAnalysis.total}
                </div>
              </div>'''

if old_str in content:
    content = content.replace(old_str, new_str)
    print("Replaced icon section")
else:
    print("Pattern not found")

# Remove Brain import if not used elsewhere
content = content.replace('  Brain,\n', '')

# Write back
with open('src/components/Layout/AppLayout.tsx', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done!")
