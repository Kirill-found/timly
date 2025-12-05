/**
 * Демо-версия дашборда результатов для скриншота
 * Табличный формат с подробной информацией о кандидатах
 */
import React from 'react';
import { MapPin, Phone, Mail, MessageCircle } from 'lucide-react';

const DemoResults: React.FC = () => {
  const mockResults = [
    {
      id: 1,
      name: 'Артём',
      surname: 'Волков',
      position: 'Senior Java Developer',
      social: '@volkov_dev',
      phone: '+7 (925) 123-4567',
      email: 'a.volkov@mail.ru',
      experience: '7 лет',
      relevance: 98,
      salary: '280 000 ₽',
      location: 'Москва, Россия',
      keyCharacteristics: 'Опытный разработчик с глубокими знаниями Spring, Hibernate. Лидерские качества.',
      finalAssessment: 'Отличный кандидат: соответствует всем требованиям, готов к релокации',
      badgeColor: 'bg-orange-500',
    },
    {
      id: 2,
      name: 'Анна',
      surname: 'Соколова',
      position: 'Middle Frontend Developer',
      social: '@sokolova_anna',
      phone: '+7 (916) 987-6543',
      email: 'anna.s@gmail.com',
      experience: '4 года',
      relevance: 92,
      salary: '180 000 ₽',
      location: 'Санкт-Петербург, Россия',
      keyCharacteristics: 'React/Vue специалист, опыт работы с TypeScript, хорошие навыки UX/UI.',
      finalAssessment: 'Хороший кандидат: немного не хватает опыта, но показывает быстрый рост',
      badgeColor: 'bg-orange-500',
    },
    {
      id: 3,
      name: 'Дмитрий',
      surname: 'Новиков',
      position: 'Senior Backend Developer',
      social: '@novikov_dev',
      phone: '+7 (903) 456-7890',
      email: 'd.novikov@mail.ru',
      experience: '6 лет',
      relevance: 89,
      salary: '250 000 ₽',
      location: 'Новосибирск, Россия',
      keyCharacteristics: 'Python/Django эксперт, опыт с микросервисами, DevOps практики.',
      finalAssessment: 'Подходящий кандидат: сильные технические навыки, но ищет удаленку',
      badgeColor: 'bg-orange-500',
    },
  ];

  const getRelevanceColor = (relevance: number) => {
    if (relevance >= 95) return 'bg-green-500';
    if (relevance >= 85) return 'bg-blue-500';
    if (relevance >= 70) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  const getRelevanceWidth = (relevance: number) => {
    return `${relevance}%`;
  };

  return (
    <div className="min-h-screen bg-white p-8">
      <div className="max-w-[1800px] mx-auto">
        {/* Header */}
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-slate-900">
            Результаты анализа резюме
          </h1>
        </div>

        {/* Table */}
        <div className="border border-slate-300 rounded-lg overflow-hidden bg-white shadow-sm">
          <table className="w-full">
            <thead className="bg-slate-50 border-b border-slate-300">
              <tr>
                <th className="text-left p-4 font-semibold text-slate-900 text-sm border-r border-slate-200">
                  Кандидат
                </th>
                <th className="text-left p-4 font-semibold text-slate-900 text-sm border-r border-slate-200">
                  Контакты
                </th>
                <th className="text-left p-4 font-semibold text-slate-900 text-sm border-r border-slate-200">
                  Опыт
                </th>
                <th className="text-left p-4 font-semibold text-slate-900 text-sm border-r border-slate-200">
                  Релевантность
                </th>
                <th className="text-left p-4 font-semibold text-slate-900 text-sm border-r border-slate-200">
                  Ожидания<br />по ЗП
                </th>
                <th className="text-left p-4 font-semibold text-slate-900 text-sm border-r border-slate-200">
                  Локация
                </th>
                <th className="text-left p-4 font-semibold text-slate-900 text-sm border-r border-slate-200">
                  Ключевые<br />характеристики
                </th>
                <th className="text-left p-4 font-semibold text-slate-900 text-sm">
                  Итоговая оценка
                </th>
              </tr>
            </thead>
            <tbody>
              {mockResults.map((result, index) => (
                <tr
                  key={result.id}
                  className={`border-b border-slate-200 hover:bg-slate-50 transition-colors ${
                    index === mockResults.length - 1 ? 'border-b-0' : ''
                  }`}
                >
                  {/* Кандидат */}
                  <td className="p-4 border-r border-slate-200">
                    <div>
                      <div className="font-bold text-slate-900 text-base mb-1">
                        {result.name}
                      </div>
                      <div className="font-bold text-slate-900 text-base mb-2">
                        {result.surname}
                      </div>
                      <div
                        className={`${result.badgeColor} text-white text-xs font-semibold px-3 py-1.5 rounded-full inline-block`}
                      >
                        {result.position}
                      </div>
                    </div>
                  </td>

                  {/* Контакты */}
                  <td className="p-4 border-r border-slate-200">
                    <div className="space-y-2 text-sm">
                      <div className="flex items-center gap-2 text-blue-600">
                        <MessageCircle className="w-4 h-4 flex-shrink-0" />
                        <span>{result.social}</span>
                      </div>
                      <div className="flex items-center gap-2 text-slate-700">
                        <Phone className="w-4 h-4 flex-shrink-0" />
                        <span>{result.phone}</span>
                      </div>
                      <div className="flex items-center gap-2 text-slate-700">
                        <Mail className="w-4 h-4 flex-shrink-0" />
                        <span>{result.email}</span>
                      </div>
                    </div>
                  </td>

                  {/* Опыт */}
                  <td className="p-4 text-slate-900 border-r border-slate-200 text-center">
                    <div className="font-medium">{result.experience}</div>
                  </td>

                  {/* Релевантность */}
                  <td className="p-4 border-r border-slate-200">
                    <div className="flex items-center gap-3">
                      <div className="flex-1">
                        <div className="h-2 bg-slate-200 rounded-full overflow-hidden">
                          <div
                            className={`h-full ${getRelevanceColor(result.relevance)} transition-all`}
                            style={{ width: getRelevanceWidth(result.relevance) }}
                          />
                        </div>
                      </div>
                      <div className="font-bold text-slate-900 text-base min-w-[3ch]">
                        {result.relevance}
                      </div>
                    </div>
                  </td>

                  {/* Ожидания по ЗП */}
                  <td className="p-4 border-r border-slate-200">
                    <div className="font-semibold text-slate-900 text-base">
                      {result.salary}
                    </div>
                  </td>

                  {/* Локация */}
                  <td className="p-4 border-r border-slate-200">
                    <div className="flex items-start gap-2 text-slate-700">
                      <MapPin className="w-4 h-4 flex-shrink-0 mt-0.5" />
                      <span className="text-sm leading-snug">{result.location}</span>
                    </div>
                  </td>

                  {/* Ключевые характеристики */}
                  <td className="p-4 border-r border-slate-200">
                    <div className="text-sm text-slate-700 leading-relaxed max-w-xs">
                      {result.keyCharacteristics}
                    </div>
                  </td>

                  {/* Итоговая оценка */}
                  <td className="p-4">
                    <div className="text-sm text-slate-700 leading-relaxed max-w-xs">
                      {result.finalAssessment}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default DemoResults;
