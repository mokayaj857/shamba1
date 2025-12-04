import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';

const resources = {
  en: {
    translation: {
      home: 'Home',
      marketplace: 'Marketplace',
      nav_market_intel: 'Market Intelligence',
      inspectors: 'Inspectors',
      dashboard: 'Dashboard',
      how_it_works: 'How It Works',

      welcome_title: 'Decentralized Land Marketplace',
      explore_marketplace: 'Explore Marketplace',
      list_your_land: 'List Your Land',

      price_forecast_title: 'Price Forecast',
      predicted_yield_metric: 'Predicted Yield (tons/ha)',
      yield_estimate: 'Yield Estimate',
      ethical_notes: 'Ethical use: data is anonymized and used for research only.'
    }
  },
  ki: {
    translation: {
      home: 'Rûri',
      marketplace: 'Mûthîrî wa mabere',
      nav_market_intel: 'Gûciarî kîrîa thî',
      inspectors: 'Makarû',
      dashboard: 'Gîtîkĩrĩre',
      how_it_works: 'Ũhoro wa gûcokia',

      welcome_title: 'Thîrî ya Gutûka ya Mûthîrî',
      explore_marketplace: 'Tûgîrîre mûthîrî',
      list_your_land: 'Rûgûrûrû rwa gwîcîra',

      price_forecast_title: 'Gûciarî kîrîa gûcokeria',
      predicted_yield_metric: 'Gûtûmîra kîrîa (t/h)',
      yield_estimate: 'Gûtûmîra',
      ethical_notes: 'Mûno wa gûcokia: îrîa data îrîa îkûmenyerwa na îkûgîa.'
    }
  },
  luo: {
    translation: {
      home: 'Nyinge',
      marketplace: 'Mareket',
      nav_market_intel: 'Gin mar Mareket',
      inspectors: 'Machony',
      dashboard: 'Tong',
      how_it_works: 'Nying gi Rati',

      welcome_title: 'Piny Mar Kendgi Maber',
      explore_marketplace: 'Timo Mareket',
      list_your_land: 'Riwoko Nodwaro',

      price_forecast_title: 'Konyo Mar Pesa',
      predicted_yield_metric: 'Jok Ma Thim (t/ha)',
      yield_estimate: 'Konyo Mar Thim',
      ethical_notes: 'Wangʼo mar bedo: data en gimoro kendo nying ma biro yudo.'
    }
  }
};

i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources,
    fallbackLng: 'en',
    interpolation: { escapeValue: false },
    react: { useSuspense: false }
  });

export default i18n;
