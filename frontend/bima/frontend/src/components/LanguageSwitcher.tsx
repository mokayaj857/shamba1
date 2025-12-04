import React, { useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';

const languages = [
  { code: 'en', label: 'English' },
  { code: 'ki', label: 'Kikuyu' },
  { code: 'luo', label: 'Luo' }
];

export default function LanguageSwitcher() {
  const { i18n } = useTranslation();
  const [query, setQuery] = useState('');

  const filtered = useMemo(() => {
    return languages.filter(l => l.label.toLowerCase().includes(query.toLowerCase()) || l.code.includes(query.toLowerCase()));
  }, [query]);

  const handleChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const code = e.target.value;
    i18n.changeLanguage(code);
  };

  return (
    <div className="flex items-center gap-2">
      <input
        aria-label="Search language"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Search"
        title="Search languages"
        className="px-2 py-1 rounded-l-md bg-white/5 text-foreground text-sm border border-r-0 border-border/20 focus:outline-none"
        style={{width: '110px'}}
      />
      <select
        value={i18n.language || 'en'}
        onChange={handleChange}
        className="px-3 py-1 rounded-r-md bg-white/5 text-foreground text-sm border border-border/20"
        title="Select language"
      >
        {filtered.map(l => (
          <option key={l.code} value={l.code}>{l.label}</option>
        ))}
      </select>
    </div>
  );
}
