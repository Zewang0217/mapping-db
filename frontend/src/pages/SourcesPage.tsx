import { useEffect, useState } from 'react';
import { Table, Button, Modal, Form, Input, Select, message, Tag, Popconfirm } from 'antd';
import { PlusOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import React from 'react';
import { Source, api_getSources, api_createSource, api_deleteSource } from '../api';

const statusColors: Record<string, string> = {
  pending: 'default',
  in_progress: 'blue',
  done: 'green',
  review: 'orange',
};

export default function SourcesPage() {
  const [sources, setSources] = useState<Source[]>([]);
  const [loading, setLoading] = useState(false);
  const [open, setOpen] = useState(false);
  const [form] = Form.useForm();
  const nav = useNavigate();

  const load = async () => {
    setLoading(true);
    try {
      const d = await api_getSources();
      setSources(d);
    } catch {
      message.error('Failed to load sources');
    }
    setLoading(false);
  };

  useEffect(() => { load(); }, []);

  const handleCreate = async () => {
    try {
      const vals = await form.validateFields();
      await api_createSource(vals);
      message.success('Source created');
      setOpen(false);
      form.resetFields();
      load();
    } catch {
      // validation error or API error — handled by form
    }
  };

  const handleDelete = async (id: number) => {
    try {
      await api_deleteSource(id);
      message.success('Source deleted');
      load();
    } catch {
      message.error('Failed to delete source');
    }
  };

  const columns = [
    { title: 'ID', dataIndex: 'id', width: 60 },
    { title: 'Name', dataIndex: 'name' },
    {
      title: 'Type',
      dataIndex: 'source_type',
      width: 100,
      render: (t: string) => {
        const color = t === 'scanner' ? 'blue' : t === 'paper' ? 'green' : 'orange';
        return <Tag color={color}>{t}</Tag>;
      },
    },
    { title: 'Categories', dataIndex: 'category_count', width: 110 },
    {
      title: 'Status',
      dataIndex: 'status',
      width: 120,
      render: (s: string) => <Tag color={statusColors[s] || 'default'}>{s}</Tag>,
    },
    { title: 'Notes', dataIndex: 'notes', ellipsis: true },
    {
      title: 'Actions',
      width: 100,
      render: (_: unknown, r: Source) => (
        <Popconfirm
          title="Delete this source and all its categories?"
          onConfirm={() => handleDelete(r.id)}
          okText="Yes"
          cancelText="No"
        >
          <Button danger size="small" onClick={(e: React.MouseEvent) => e.stopPropagation()}>
            Delete
          </Button>
        </Popconfirm>
      ),
    },
  ];

  return (
    <>
      <Button
        type="primary"
        icon={<PlusOutlined />}
        onClick={() => setOpen(true)}
        style={{ marginBottom: 16 }}
      >
        Add Source
      </Button>
      <Table
        dataSource={sources}
        rowKey="id"
        columns={columns}
        loading={loading}
        onRow={(r: Source) => ({
          onClick: () => nav(`/sources/${r.id}`),
          style: { cursor: 'pointer' },
        })}
        pagination={{ pageSize: 20 }}
      />
      <Modal
        title="Add Source"
        open={open}
        onOk={handleCreate}
        onCancel={() => {
          setOpen(false);
          form.resetFields();
        }}
      >
        <Form form={form} layout="vertical">
          <Form.Item name="name" label="Name" rules={[{ required: true, message: 'Name is required' }]}>
            <Input />
          </Form.Item>
          <Form.Item
            name="source_type"
            label="Type"
            rules={[{ required: true, message: 'Type is required' }]}
          >
            <Select
              options={[
                { value: 'scanner', label: 'Scanner' },
                { value: 'paper', label: 'Paper' },
                { value: 'report', label: 'Report' },
              ]}
            />
          </Form.Item>
          <Form.Item name="url" label="URL">
            <Input />
          </Form.Item>
          <Form.Item name="notes" label="Notes">
            <Input.TextArea rows={3} />
          </Form.Item>
        </Form>
      </Modal>
    </>
  );
}
