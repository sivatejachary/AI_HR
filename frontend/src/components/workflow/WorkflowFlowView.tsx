'use client';

import React, { useState, useCallback } from 'react';
import {
  ReactFlow,
  Controls,
  Background,
  applyNodeChanges,
  applyEdgeChanges,
  Node,
  Edge,
  Handle,
  Position
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import { WorkflowStep } from '../../types';
import { UserCheck, Bot, PhoneCall, Mail, Calendar, Code2, FileCheck, CheckCircle2, ShieldAlert, Sparkles, Sliders } from 'lucide-react';

const categoryIcons: Record<string, any> = {
  Screening: Bot,
  Communication: PhoneCall,
  Assessment: Code2,
  Interview: UserCheck,
  Decision: CheckCircle2,
  Other: FileCheck
};

// Clean enterprise card node for Flow View
function EnterpriseStepNode({ data }: any) {
  const Icon = categoryIcons[data.category] || Sliders;

  return (
    <div
      className={`px-4 py-3 rounded-xl border bg-white shadow-xs min-w-[240px] transition ${
        data.isSelected ? 'ring-2 ring-blue-600 border-blue-600' : 'border-gray-300 hover:border-gray-400'
      }`}
    >
      <Handle type="target" position={Position.Top} className="!bg-blue-600 !w-2.5 !h-2.5" />
      <div className="flex items-center justify-between gap-2 border-b border-gray-100 pb-2">
        <div className="flex items-center gap-2">
          <div className="w-6 h-6 rounded-md bg-blue-50 text-blue-700 flex items-center justify-center font-bold text-xs">
            {data.order}
          </div>
          <span className="text-xs font-bold text-gray-900 line-clamp-1">{data.label}</span>
        </div>
        <span className="text-[10px] px-1.5 py-0.5 rounded font-medium bg-gray-100 text-gray-700">
          {data.automation}
        </span>
      </div>
      
      <div className="mt-2 flex items-center justify-between text-[11px] text-gray-500">
        <span className="flex items-center gap-1 font-medium text-gray-700">
          <Icon size={12} className="text-gray-400" /> {data.category}
        </span>
        <span className="font-semibold text-gray-600">Owner: {data.owner}</span>
      </div>
      <Handle type="source" position={Position.Bottom} className="!bg-blue-600 !w-2.5 !h-2.5" />
    </div>
  );
}

const nodeTypes = { enterpriseStep: EnterpriseStepNode };

interface Props {
  steps: WorkflowStep[];
  selectedStepId: string | null;
  onSelectStep: (id: string) => void;
}

export function WorkflowFlowView({ steps, selectedStepId, onSelectStep }: Props) {
  const initialNodes: Node[] = steps.map((s, idx) => ({
    id: s.id,
    type: 'enterpriseStep',
    position: { x: 250, y: idx * 120 + 30 },
    data: {
      label: s.name,
      order: idx + 1,
      category: s.category,
      owner: s.owner,
      automation: s.automation,
      isSelected: s.id === selectedStepId
    }
  }));

  const initialEdges: Edge[] = steps.slice(0, -1).map((s, idx) => ({
    id: `e-${s.id}-${steps[idx + 1].id}`,
    source: s.id,
    target: steps[idx + 1].id,
    animated: true,
    style: { stroke: '#1D4ED8', strokeWidth: 2 }
  }));

  const [nodes, setNodes] = useState<Node[]>(initialNodes);
  const [edges, setEdges] = useState<Edge[]>(initialEdges);

  const onNodesChange = useCallback((changes: any) => setNodes((nds) => applyNodeChanges(changes, nds)), []);
  const onEdgesChange = useCallback((changes: any) => setEdges((eds) => applyEdgeChanges(changes, eds)), []);

  const onNodeClick = (_: any, node: Node) => {
    onSelectStep(node.id);
  };

  return (
    <div className="w-full h-full bg-[#F8F9FB] border border-gray-200 rounded-xl relative overflow-hidden">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onNodeClick={onNodeClick}
        nodeTypes={nodeTypes}
        fitView
      >
        <Background color="#E5E7EB" gap={20} />
        <Controls />
      </ReactFlow>
    </div>
  );
}
