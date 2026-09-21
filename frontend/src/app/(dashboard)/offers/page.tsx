'use client';

import React from 'react';
import { useHRState } from '../../../stores/useHRStore';
import { FileCheck2, Send, CheckCircle2 } from 'lucide-react';
import { EmptyState } from '../../../components/ui/EmptyState';

export default function OffersPage() {
  const hrState = useHRState();

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-white p-6 rounded-lg border border-gray-200 shadow-xs">
        <div>
          <h1 className="text-2xl font-semibold text-gray-900 tracking-tight flex items-center gap-2">
            <FileCheck2 size={22} className="text-blue-900" /> Candidate Offers Management
          </h1>
          <p className="text-xs text-gray-500 mt-1">
            Manage offer letter approvals and automated candidate dispatch.
          </p>
        </div>
      </div>

      {hrState.offers.length === 0 ? (
        <EmptyState
          icon={FileCheck2}
          title="No offer letters yet"
          description="Offer letters will appear here when candidates successfully pass interview stages and evaluations."
        />
      ) : (
        <div className="bg-white border border-gray-200 rounded-lg overflow-hidden shadow-xs">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className="bg-gray-50 border-b border-gray-200 text-gray-600 font-semibold uppercase tracking-wider text-[11px]">
                  <th className="py-3 px-4">Candidate</th>
                  <th className="py-3 px-4">Job Position</th>
                  <th className="py-3 px-4">Compensation</th>
                  <th className="py-3 px-4">Start Date</th>
                  <th className="py-3 px-4">Approval</th>
                  <th className="py-3 px-4">Status</th>
                  <th className="py-3 px-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200 text-gray-700">
                {hrState.offers.map((off) => (
                  <tr key={off.id} className="hover:bg-gray-50/80 transition">
                    <td className="py-3 px-4 font-semibold text-gray-900">{off.candidateName}</td>
                    <td className="py-3 px-4 text-gray-700 font-medium">{off.jobTitle}</td>
                    <td className="py-3 px-4 text-emerald-700 font-semibold">{off.salary}</td>
                    <td className="py-3 px-4 text-gray-600">{off.startDate}</td>
                    <td className="py-3 px-4">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase border ${
                        off.approvalStatus === 'APPROVED' ? 'bg-emerald-50 text-emerald-800 border-emerald-200' : 'bg-amber-50 text-amber-800 border-amber-200'
                      }`}>
                        {off.approvalStatus}
                      </span>
                    </td>
                    <td className="py-3 px-4">
                      <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase bg-blue-50 text-blue-800 border border-blue-200">
                        {off.status}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-right">
                      <div className="flex items-center justify-end gap-2">
                        {off.status === 'DRAFT' || off.approvalStatus === 'PENDING' ? (
                          <button
                            onClick={() => hrState.approveOffer(off.id)}
                            className="px-3 py-1 bg-emerald-700 hover:bg-emerald-800 text-white rounded text-xs font-medium transition"
                          >
                            Approve Offer
                          </button>
                        ) : (
                          <button
                            onClick={() => hrState.sendOfferEmail(off.id)}
                            className="px-3 py-1 bg-blue-900 hover:bg-blue-800 text-white rounded text-xs font-medium flex items-center gap-1 transition"
                          >
                            <Send size={12} /> Dispatch Offer
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
