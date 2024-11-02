import React from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { AlertTriangle } from 'lucide-react';

const TokenCostVisualization = () => {
  // Average tokens per message
  const avgTokens = [
    {
      name: 'Enska',
      tokens: 14,
      cost: (14 * 2.50) / 1000000
    },
    {
      name: 'Íslenska',
      tokens: 40,
      cost: (40 * 2.50) / 1000000
    }
  ];

  // Sample comparison data
  const sampleText = {
    en: "The committee decided to postpone the meeting until next Wednesday.",
    is: "Þingið ákvað að fresta fundinum til næstu miðvikudags.",
    enTokens: 17,
    isTokens: 46
  };

  // Calculate monthly costs for different usage scenarios for GPT-4O
  const calculateMonthlyCost = (messagesPerDay, tokens) => {
    const inputCost = (tokens * 2.50) / 1000000; // GPT-4O input cost per message ($2.50 per 1M tokens)
    const outputCost = (tokens * 4 * 10.00) / 1000000; // Assuming output is 4x input length ($10.00 per 1M tokens)
    return (inputCost + outputCost) * messagesPerDay * 30;
  };

  const usageScenarios = [
    {
      name: 'Lítil notkun',
      messages: 10,
      englishCost: calculateMonthlyCost(10, 14).toFixed(2),
      icelandicCost: calculateMonthlyCost(10, 40).toFixed(2)
    },
    {
      name: 'Meðal notkun',
      messages: 50,
      englishCost: calculateMonthlyCost(50, 14).toFixed(2),
      icelandicCost: calculateMonthlyCost(50, 40).toFixed(2)
    },
    {
      name: 'Mikil notkun',
      messages: 200,
      englishCost: calculateMonthlyCost(200, 14).toFixed(2),
      icelandicCost: calculateMonthlyCost(200, 40).toFixed(2)
    }
  ];

  return (
    <div className="space-y-8 w-full max-w-4xl mx-auto p-4">
      <Card>
        <CardHeader>
          <CardTitle className="text-2xl font-bold">**Dýr íslenska: Kostnaðargreining á GPT-4o notkun**</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-6">
            <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4">
              <div className="flex">
                <div className="flex-shrink-0">
                  <AlertTriangle className="h-5 w-5 text-yellow-400" />
                </div>
                <div className="ml-3">
                  <p className="text-sm text-yellow-700">
                    Íslenska notar að meðaltali 187% fleiri tókena en enska, sem hefur bein áhrif á kostnað við notkun málgerðarlíkana eins og GPT-4.
                  </p>
                </div>
              </div>
            </div>

            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart
                  data={avgTokens}
                  margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
                >
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis label={{ value: 'Meðalfjöldi tókena', angle: -90, position: 'insideLeft' }} />
                  <Tooltip />
                  <Bar dataKey="tokens" fill="#3b82f6" name="Tóken per skilaboð" />
                </BarChart>
              </ResponsiveContainer>
            </div>

            <div className="mt-6">
              <h3 className="text-lg font-semibold mb-4">Mánaðarlegur kostnaður eftir notkun</h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {usageScenarios.map((scenario) => (
                  <div key={scenario.name} className="border rounded-lg p-4">
                    <h4 className="font-medium mb-2">{scenario.name}</h4>
                    <p className="text-sm text-gray-600">{scenario.messages} skilaboð á dag</p>
                    <div className="mt-2">
                      <p className="text-sm">Enska: ${scenario.englishCost}</p>
                      <p className="text-sm">Íslenska: ${scenario.icelandicCost}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="mt-6">
              <h3 className="text-lg font-semibold mb-4">Dæmi um tókenanotkun</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="border rounded-lg p-4">
                  <h4 className="font-medium mb-2">Enska: {sampleText.enTokens} tóken</h4>
                  <p className="text-sm">{sampleText.en}</p>
                </div>
                <div className="border rounded-lg p-4">
                  <h4 className="font-medium mb-2">Íslenska: {sampleText.isTokens} tóken</h4>
                  <p className="text-sm">{sampleText.is}</p>
                </div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default TokenCostVisualization;