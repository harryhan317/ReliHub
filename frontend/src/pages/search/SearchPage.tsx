import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { TopBar, TabBar } from '../../layouts/Components';
import { Card, Tag } from '../../components/ui/Common';
import { searchService } from '../../services/otherServices';

const hotKeywords = ['降额设计', 'HALT测试', 'FMEA', 'ESD防护', '可靠性增长', 'PCB设计', 'MTBF计算', '环境试验'];

const SearchPage: React.FC = () => {
  const navigate = useNavigate();
  const [query, setQuery] = useState('');
  const [activeTab, setActiveTab] = useState(0);
  const [searchHistory, setSearchHistory] = useState<string[]>(['电容降额设计规范', 'HALT测试方案', 'FMEA表格']);
  const [hasSearched, setHasSearched] = useState(false);
  const tabs = ['资源', '社区', '爱问'];

  const handleSearch = async (text?: string) => {
    const q = text || query.trim();
    if (!q) return;
    setQuery(q);
    setHasSearched(true);
    if (!searchHistory.includes(q)) {
      setSearchHistory([q, ...searchHistory.slice(0, 9)]);
    }
    try {
      const typeMap = ['RESOURCE', 'COMMUNITY', 'AI'];
      await searchService.search({ query: q, type: typeMap[activeTab] });
    } catch {}
  };

  const clearHistory = async () => {
    setSearchHistory([]);
    try { await searchService.clearSearchHistory(); } catch {}
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

      <TabBar tabs={tabs} activeIndex={activeTab} onTabChange={setActiveTab} />

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
                    <div key={i} className="history-item" style={{ padding: 'var(--spacing-sm) 0', border: 'none' }}>
                      <div className="history-item-content">
                        <div className="history-item-title" style={{ fontWeight: 400 }}>{h}</div>
                      </div>
                      <span style={{ color: 'var(--color-text-muted)', cursor: 'pointer' }} onClick={() => setSearchHistory(searchHistory.filter((_, idx) => idx !== i))}>✕</span>
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
            <div className="empty-state">
              <div className="empty-state-icon">🔍</div>
              <div className="empty-state-text">暂无搜索结果</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default SearchPage;
