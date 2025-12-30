with open('UploadCandidates.tsx', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find return line
start_idx = None
for i, line in enumerate(lines):
    if '  return (' in line:
        start_idx = i
        break

new_return = '''  return (
    <>
      <div className="panel" style={{ marginBottom: 24 }}>
        <div className="panel-header">
          <span className="panel-title">Загрузка резюме</span>
          <div className="panel-actions">
            <select className="filter-btn" value={selectedVacancy} onChange={(e) => setSelectedVacancy(e.target.value)} style={{ background: 'transparent', border: '1px solid var(--border)', cursor: 'pointer', color: 'var(--text)' }}>
              <option value="">Без вакансии</option>
              {vacancies.map(v => (<option key={v.id} value={v.id}>{v.title}</option>))}
            </select>
          </div>
        </div>
        <div className="upload-zone" onDragOver={handleDragOver} onDragLeave={handleDragLeave} onDrop={handleDrop} onClick={() => !isUploading && document.getElementById('file-upload')?.click()} style={{ margin: 16, borderColor: isDragging ? 'var(--text-secondary)' : undefined, background: isDragging ? 'var(--bg-hover)' : undefined, cursor: isUploading ? 'default' : 'pointer' }}>
          {isUploading ? (
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 16 }}>
              <Loader2 style={{ width: 40, height: 40, animation: 'spin 1s linear infinite', color: 'var(--text-tertiary)' }} />
              <div className="upload-title">Загрузка...</div>
              <div style={{ width: 200, height: 4, background: 'var(--border)', borderRadius: 2 }}><div style={{ width: uploadProgress + '%', height: '100%', background: 'var(--text)', transition: 'width 0.3s' }} /></div>
            </div>
          ) : (
            <>
              <div style={{ display: 'flex', justifyContent: 'center', gap: 16, marginBottom: 16 }}>
                <FileText style={{ width: 32, height: 32, color: 'var(--red)' }} />
                <FileSpreadsheet style={{ width: 32, height: 32, color: 'var(--green)' }} />
              </div>
              <div className="upload-title">Перетащите файлы сюда</div>
              <div className="upload-desc">PDF, XLSX, XLS - макс. 10 MB</div>
              <input type="file" id="file-upload" style={{ display: 'none' }} accept=".pdf,.xlsx,.xls" multiple onChange={(e) => handleFileUpload(e.target.files)} />
            </>
          )}
        </div>
      </div>
      <div className="panel">
        <div className="panel-header">
          <span className="panel-title">Кандидаты ({candidates.length})</span>
          <div className="panel-actions">
            {(['all', 'hire', 'interview', 'reject'] as const).map(filter => (<button key={filter} className={'panel-btn ' + (recommendationFilter === filter ? 'active' : '')} onClick={() => { setRecommendationFilter(filter); setTimeout(loadCandidates, 0); }}>{filter === 'all' ? 'Все' : filter === 'hire' ? 'Нанять' : filter === 'interview' ? 'Интервью' : 'Отказ'}</button>))}
          </div>
        </div>
        <div className="table-container">
          {isLoading ? (<div style={{ display: 'flex', justifyContent: 'center', padding: 48 }}><Loader2 style={{ width: 24, height: 24, animation: 'spin 1s linear infinite', color: 'var(--text-tertiary)' }} /></div>) : candidates.length === 0 ? (<div style={{ textAlign: 'center', padding: 48, color: 'var(--text-tertiary)' }}><Upload style={{ width: 40, height: 40, margin: '0 auto 16px', opacity: 0.3 }} /><div style={{ fontSize: 13 }}>Нет загруженных кандидатов</div></div>) : (
            <table className="data-table">
              <thead><tr><th>Кандидат</th><th>Контакты</th><th>Опыт</th><th>Балл</th><th>Статус</th><th></th></tr></thead>
              <tbody>
                {candidates.map(candidate => (<tr key={candidate.id}>
                  <td><div className="candidate"><div className="candidate-avatar">{candidate.full_name?.[0]?.toUpperCase() || '?'}</div><div><div className="candidate-name">{candidate.full_name}</div><div className="candidate-role">{candidate.title || '—'}</div></div></div></td>
                  <td><div style={{ fontSize: 12, color: 'var(--text-secondary)' }}>{candidate.email || candidate.phone || '—'}</div></td>
                  <td><span style={{ color: 'var(--text-secondary)', fontSize: 12 }}>{candidate.experience_years ? candidate.experience_years + ' лет' : '—'}</span></td>
                  <td>{candidate.ai_score ? <span className={'score ' + (candidate.ai_score >= 80 ? 'high' : candidate.ai_score >= 60 ? 'mid' : 'low')}>{candidate.ai_score}</span> : '—'}</td>
                  <td>{candidate.is_analyzed ? <span className={'tag ' + (candidate.ai_recommendation === 'hire' ? 'tag-hire' : candidate.ai_recommendation === 'interview' ? 'tag-interview' : candidate.ai_recommendation === 'reject' ? 'tag-reject' : 'tag-maybe')}>{candidate.ai_recommendation === 'hire' ? 'Нанять' : candidate.ai_recommendation === 'interview' ? 'Интервью' : candidate.ai_recommendation === 'reject' ? 'Отказ' : 'Возможно'}</span> : <span className="tag" style={{ background: 'var(--bg-hover)', color: 'var(--text-tertiary)' }}>Ожидает</span>}</td>
                  <td><div style={{ display: 'flex', gap: 4 }}><button className="action-btn" onClick={() => toggleFavorite(candidate)}>{candidate.is_favorite ? <Star style={{ width: 14, height: 14, fill: 'var(--yellow)', color: 'var(--yellow)' }} /> : <StarOff style={{ width: 14, height: 14 }} />}</button>{!candidate.is_analyzed && selectedVacancy && <button className="action-btn" onClick={() => analyzeCandidate(candidate.id, selectedVacancy)}><Brain style={{ width: 14, height: 14 }} /></button>}<button className="action-btn" onClick={() => deleteCandidate(candidate.id)} style={{ color: 'var(--red)' }}><Trash2 style={{ width: 14, height: 14 }} /></button></div></td>
                </tr>))}
              </tbody>
            </table>
          )}
        </div>
      </div>
      <style>{`@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }`}</style>
    </>
  );
};

export default UploadCandidates;
'''

new_content = ''.join(lines[:start_idx]) + new_return
with open('UploadCandidates.tsx', 'w', encoding='utf-8') as f:
    f.write(new_content)
print('Done')
