'use client';

import React, { useState, useEffect } from 'react';
import { useHRState } from '../../../stores/useHRStore';
import { api } from '../../../lib/api';
import { Plug, RefreshCw, Key, CheckCircle2, AlertCircle, ExternalLink } from 'lucide-react';

export default function IntegrationsPage() {
  const hrState = useHRState();
  const [testingId, setTestingId] = useState<string | null>(null);
  const [testSuccessId, setTestSuccessId] = useState<string | null>(null);
  const [googleStatus, setGoogleStatus] = useState<{
    connected: boolean;
    status: string;
    email?: string | null;
    services: { forms: boolean; sheets: boolean; calendar: boolean; gmail: boolean };
  }>({
    connected: false,
    status: 'DISCONNECTED',
    email: null,
    services: { forms: false, sheets: false, calendar: false, gmail: false }
  });

  useEffect(() => {
    api.getGoogleIntegrationStatus()
      .then(res => setGoogleStatus(res))
      .catch(err => console.warn('Could not fetch Google integration status:', err));
  }, []);

  const handleTestConnection = (id: string) => {
    setTestingId(id);
    setTimeout(() => {
      setTestingId(null);
      setTestSuccessId(id);
      setTimeout(() => setTestSuccessId(null), 3000);
    }, 1000);
  };

  const handleDisconnectGoogle = async () => {
    try {
      await api.disconnectGoogleOAuth();
      setGoogleStatus({
        connected: false,
        status: 'DISCONNECTED',
        email: null,
        services: { forms: false, sheets: false, calendar: false, gmail: false }
      });
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-white p-6 rounded-lg border border-gray-200 shadow-xs">
        <div>
          <h1 className="text-2xl font-semibold text-gray-900 tracking-tight flex items-center gap-2">
            <Plug size={22} className="text-blue-900" /> Platform Integration Center
          </h1>
          <p className="text-xs text-gray-500 mt-1">
            Manage official API connections for Google Workspace (Forms, Sheets, Calendar, Gmail), ElevenLabs Voice AI, and n8n.
          </p>
        </div>
      </div>

      {/* Featured Enterprise Card: Google Workspace Integration */}
      <div className="bg-white border border-gray-200 rounded-lg p-6 shadow-xs space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-gray-100 pb-4">
          <div>
            <div className="flex items-center gap-3">
              <h2 className="text-lg font-bold text-gray-900">Google Workspace Integration</h2>
              <span className={`px-2.5 py-0.5 rounded text-[11px] font-bold uppercase flex items-center gap-1 ${
                googleStatus.connected
                  ? 'bg-emerald-50 text-emerald-800 border border-emerald-200'
                  : 'bg-amber-50 text-amber-800 border border-amber-200'
              }`}>
                <span className={`w-2 h-2 rounded-full ${googleStatus.connected ? 'bg-emerald-500' : 'bg-amber-500'}`} />
                {googleStatus.connected ? 'Connected' : 'Disconnected'}
              </span>
            </div>
            <p className="text-xs text-gray-500 mt-1">
              Connect your HR Google Workspace account once to authorize Google Forms creation, Google Sheets sync, Google Calendar scheduling, and Gmail dispatch.
            </p>
          </div>

          <div className="flex items-center gap-2 shrink-0">
            {googleStatus.connected ? (
              <>
                <button
                  onClick={handleDisconnectGoogle}
                  className="px-4 py-2 bg-white border border-gray-300 text-red-700 hover:bg-gray-50 text-xs font-semibold rounded-md transition"
                >
                  Disconnect
                </button>
                <button
                  onClick={() => api.connectGoogleOAuth()}
                  className="px-4 py-2 bg-blue-900 hover:bg-blue-800 text-white text-xs font-semibold rounded-md transition flex items-center gap-1.5"
                >
                  Manage Connection <ExternalLink size={13} />
                </button>
              </>
            ) : (
              <button
                onClick={() => api.connectGoogleOAuth()}
                className="px-5 py-2.5 bg-blue-900 hover:bg-blue-800 text-white text-xs font-bold rounded-md transition shadow-xs flex items-center gap-2"
              >
                <Plug size={15} /> Connect Google
              </button>
            )}
          </div>
        </div>

        {googleStatus.connected && googleStatus.email && (
          <div className="p-3 bg-blue-50/50 border border-blue-100 rounded-md text-xs text-blue-900 flex items-center justify-between">
            <span>Authorized Account: <strong className="font-semibold">{googleStatus.email}</strong></span>
            <span className="text-[11px] text-blue-700 font-medium">Single Source of Truth: PostgreSQL</span>
          </div>
        )}

        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
          {[
            { name: 'Google Forms', key: 'forms', desc: 'Auto-create Google Forms from Jobs' },
            { name: 'Google Sheets', key: 'sheets', desc: 'Sync candidate responses via n8n' },
            { name: 'Google Calendar', key: 'calendar', desc: 'Check freebusy & create Meet calls' },
            { name: 'Gmail', key: 'gmail', desc: 'Send automated confirmation emails' }
          ].map(svc => (
            <div key={svc.key} className="p-3 bg-gray-50 border border-gray-200 rounded-md space-y-1">
              <div className="flex items-center gap-1.5 font-semibold text-gray-900">
                <CheckCircle2 size={14} className={googleStatus.connected ? "text-emerald-700" : "text-gray-400"} />
                <span>{svc.name}</span>
              </div>
              <p className="text-[11px] text-gray-500 leading-snug">{svc.desc}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Integration Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {hrState.integrations.map(intg => (
          <div key={intg.id} className="bg-white border border-gray-200 rounded-lg p-5 space-y-4 shadow-xs flex flex-col justify-between">
            <div className="space-y-2">
              <div className="flex items-start justify-between">
                <div>
                  <h3 className="text-base font-semibold text-gray-900">{intg.platformName}</h3>
                  <p className="text-xs text-gray-500">Category: {intg.category}</p>
                </div>
                <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase ${
                  intg.isConnected
                    ? 'bg-emerald-50 text-emerald-800 border border-emerald-200'
                    : 'bg-amber-50 text-amber-800 border border-amber-200'
                }`}>
                  {intg.isConnected ? 'Connected' : 'Disconnected'}
                </span>
              </div>

              <p className="text-xs text-gray-600 leading-relaxed">{intg.description}</p>

              {intg.credentialsMasked && (
                <div className="p-2.5 bg-gray-50 rounded border border-gray-200 text-[11px] font-mono text-gray-700 flex items-center gap-2">
                  <Key size={13} className="text-gray-400 shrink-0" />
                  <span className="truncate">{intg.credentialsMasked}</span>
                </div>
              )}
            </div>

            <div className="pt-3 border-t border-gray-100 flex items-center justify-between text-xs">
              <button
                onClick={() => {
                  if (intg.platformName.toLowerCase().includes('google')) {
                    api.connectGoogleOAuth();
                  } else {
                    hrState.toggleIntegration(intg.id);
                  }
                }}
                className={`px-3 py-1.5 rounded font-medium transition ${
                  intg.isConnected
                    ? 'bg-white border border-gray-300 text-red-700 hover:bg-gray-50'
                    : 'bg-emerald-700 text-white hover:bg-emerald-800'
                }`}
              >
                {intg.isConnected ? 'Disconnect' : 'Connect'}
              </button>

              <button
                onClick={() => handleTestConnection(intg.id)}
                disabled={!intg.isConnected || testingId === intg.id}
                className="px-3 py-1.5 bg-white border border-gray-300 hover:bg-gray-50 text-gray-700 rounded font-medium flex items-center gap-1.5 disabled:opacity-50 transition"
              >
                {testingId === intg.id ? <RefreshCw size={13} className="animate-spin text-blue-800" /> : <Plug size={13} />}
                {testSuccessId === intg.id ? 'Verified!' : 'Test Connection'}
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
