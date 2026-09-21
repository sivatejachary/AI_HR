'use client';

import React, { use } from 'react';
import { useHRState } from '../../../../stores/useHRStore';
import { WorkflowEditor } from '../../../../components/workflow/WorkflowEditor';
import { ArrowLeft, GitFork } from 'lucide-react';
import Link from 'next/link';

export default function WorkflowDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const resolvedParams = use(params);
  const hrState = useHRState();

  const workflow = hrState.workflows.find(w => w.id === resolvedParams.id);

  if (!workflow) {
    return (
      <div className="max-w-4xl mx-auto p-12 text-center space-y-4">
        <GitFork size={36} className="mx-auto text-gray-400" />
        <h2 className="text-base font-bold text-gray-900">Workflow Not Found</h2>
        <p className="text-xs text-gray-500">The requested hiring workflow does not exist or has been removed.</p>
        <Link
          href="/workflows"
          className="inline-flex items-center gap-1.5 px-4 py-2 bg-blue-700 text-white rounded-lg text-xs font-semibold"
        >
          <ArrowLeft size={14} /> Return to Hiring Workflows
        </Link>
      </div>
    );
  }

  return (
    <div className="h-[calc(100vh-100px)] flex flex-col">
      <div className="mb-2">
        <Link
          href="/workflows"
          className="text-xs font-semibold text-gray-600 hover:text-gray-900 flex items-center gap-1 inline-flex"
        >
          <ArrowLeft size={13} /> Back to Workflows
        </Link>
      </div>

      <div className="flex-1 overflow-hidden">
        <WorkflowEditor
          key={workflow.id}
          workflow={workflow}
          onSaveWorkflow={(updatedSteps) => hrState.updateWorkflowSteps(workflow.id, updatedSteps)}
        />
      </div>
    </div>
  );
}
