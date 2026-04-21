import React, { useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { TopBar, TabBar } from '../../layouts/Components';
import { Card, Tag } from '../../components/ui/Common';
import { searchService } from '../../services/otherServices';

const hotKeywords = ['降额设计', 'HALT测试', 'FMEA', 'ESD防护', '可靠性增长', 'PCB设计', 'MTBF计算', '环境试验'];

interface SearchResult {
  id: string;
  title: string;
  desc: string;
  type: string;
  extra: string;
}

const SearchPage: React.FC = () => {
  const navigate = useNavigate();
  const [query, setQuery] = useState('');
  const [activeTab, setActiveTab] = useState(0);
  const [searchHistory, setSearchHistory] = useState<string[]>(() => {
    try {
      return JSON.parse(localStorage.getItem('search_history') || '[]');
    } catch { return []; }
  });
  const [hasSearched, setHasSearched] = useState(false);
  const [results, setResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const tabs = ['资源', '社区', '爱问'];

  const saveHistory = (history: string[]) => {
    setSearchHistory(history);
    localStorage.setItem('search_history', JSON.stringify(history));
  };

  const handleSearch = useCallback(async (text?: string) => {
    const q = text || query.trim();
    if (!q) return;
    setQuery(q);
    setHasSearched(true);
    if (!searchHistory.includes(q)) {
      saveHistory([q, ...searchHistory.slice(0, 9)]);
    }
    setLoading(true);
    try {
      const typeMap = ['RESOURCE', 'COMMUNITY', 'AI'] as const;
      const res = await searchService.search({ query: q, type: typeMap[activeTab] });
      if (res.data?.items) {
        setResults(res.data.items.map((item: any) => ({
          id: item.id,
          title: item.title || item.content?.substring(0, 30) || '',
          desc: item.description || item.content?.substring(0, 80) || '',
          type: item.type || typeMap[activeTab],
          extra: item.download_count != null ? `📥${item.download_count}` : item.reply_count != null ? `💬${item.reply_count}` : '',
        })));
      } else {
        setResults([]);
      }
    } catch {
      setResults([]);
    } finally {
      setLoading(false);
    }
  }, [query, activeTab, searchHistory]);

  const clearHistory = async () => {
    saveHistory([]);
    try { await searchService.clearSearchHistory(); } catch {}
  };

  const handleResultClick = (result: SearchResult) => {
    if (result.type === 'RESOURCE') navigate(`/resource/${result.id}`);
    else if (result.type === 'COMMUNITY') navigate(`/community/topic/${result.id}`);
    else if (result.type === 'AI') navigate(`/chat/${result.id}`);
  };

  return (
    <div className="page active">
      <div className="top-bar">
        <button className="top-bar-btn" onClick={() => navigate(-1)}>←</button>
        <div className="search-input-wrapper" style={{ flex: 1 }}>
          <span className="search-icon">🔍</span>
          <input
            type="text"
            placeholder="搜索"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
            autoFocus
          />
          {query && (
            <button className="top-bar-btn" style={{ width: 24, height: 24, fontSize: 14 }} onClick={() => setQuery('')}>✕</button>
          )}
        </div>
        <button className="top-bar-btn" onClick={() => handleSearch()} style={{ color: 'var(--color-accent)', fontWeight: 600, fontSize: 'var(--font-size-body)', width: 'auto' }}>搜索</button>
      </div>

      <TabBar tabs={tabs} activeIndex={activeTab} onTabChange={(tab) => { setActiveTab(tab); if (hasSearched) handleSearch(); }} />

      {!hasSearched ? (
        <div className="content-area-no-nav">
          <div style={{ padding: 'var(--spacing-lg)' }}>
            <div className="section-header" style={{ padding: '0 0 var(--spacing-md)' }}>
              <div className="section-title" style={{ fontSize: 'var(--font-size-body)' }}>🔥 热门搜索</div>
            </div>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 'var(--spacing-sm)' }}>
              {hotKeywords.map((kw) => (
                <Tag key={kw} variant="accent" style={{ cursor: 'pointer' }} onClick={() => handleSearch(kw)}>{kw}</Tag>
              ))}
            </div>

            {searchHistory.length > 0 && (
              <>
                <div className="section-header" style={{ padding: 'var(--spacing-xl) 0 var(--spacing-md)' }}>
                  <div className="section-title" style={{ fontSize: 'var(--font-size-body)' }}>🕐 搜索历史</div>
                  <span className="section-action" onClick={clearHistory}>清空</span>
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-sm)' }}>
                  {searchHistory.map((h, i) => (
                    <div key={i} className="history-item" style={{ padding: 'var(--spacing-sm) 0', border: 'none', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <div className="history-item-content" style={{ cursor: 'pointer' }} onClick={() => handleSearch(h)}>
                        <div className="history-item-title" style={{ fontWeight: 400 }}>{h}</div>
                      </div>
                      <span style={{ color: 'var(--color-text-muted)', cursor: 'pointer' }} onClick={() => saveHistory(searchHistory.filter((_, idx) => idx !== i))}>✕</span>
                    </div>
                  ))}
                </div>
              </>
            )}
          </div>
        </div>
      ) : (
        <div className="content-area-no-nav">
          <div style={{ padding: 'var(--spacing-lg)' }}>
            <div style={{ fontSize: 'var(--font-size-caption)', color: 'var(--color-text-muted)', marginBottom: 'var(--spacing-md)' }}>
              搜索 "{query}" 的结果
            </div>
            {loading ? (
              <div style={{ textAlign: 'center', padding: 'var(--spacing-2xl)', color: 'var(--color-text-muted)' }}>
                <div style={{ fontSize: 32, marginBottom: 8 }}>⏳</div>
                <div>搜索中...</div>
              </div>
            ) : results.length > 0 ? (
              <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-md)' }}>
                {results.map((result) => (
                  <Card key={result.id} className="resource-card" onClick={() => handleResultClick(result)}>
                    <div className="resource-title">{result.title}</div>
                    <div className="resource-desc" style={{ fontSize: 'var(--font-size-small)', color: 'var(--color-text-tertiary)', marginTop: 4, lineHeight: 'var(--line-height-body)' }}>
                      {result.desc}
                    </div>
                    {result.extra && (
                      <div className="resource-meta" style={{ marginTop: 4 }}>
                        <span>{result.extra}</span>
                      </div>
                    )}
                  </Card>
                ))}
              </div>
            ) : (
              <div className="empty-state">
                <div className="empty-state-icon">🔍</div>
                <div className="empty-state-text">暂无搜索结果</div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default SearchPage;
