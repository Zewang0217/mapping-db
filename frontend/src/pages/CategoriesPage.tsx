import { useEffect, useState, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Table, Button, Modal, Form, Input, Select, Tag, message, Space, Breadcrumb } from 'antd';
import { PlusOutlined, ArrowLeftOutlined, DeleteOutlined } from '@ant-design/icons';
import {
  Category,
  Mapping,
  DimValue,
  api_getCategories,
  api_createCategory,
  api_getMapping,
  api_updateMapping,
  api_getDimValues,
  api_deleteCategory,
  api_updateCategory,

} from '../api';

export default function CategoriesPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const sourceId = Number(id);
  const [cats, setCats] = useState<Category[]>([]);
  const [mappings, setMappings] = useState<Record<number, Mapping>>({});
  const [dimVals, setDimVals] = useState<DimValue[]>([]);
  const [loading, setLoading] = useState(false);
  const [open, setOpen] = useState(false);
  const [form] = Form.useForm();

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const [c, dv] = await Promise.all([
        api_getCategories(sourceId),
        api_getDimValues(),
      ]);
      setCats(c);
      setDimVals(dv);

      // Fetch all mappings in parallel (handle 404s gracefully)
      const ms: Record<number, Mapping> = {};
      const results = await Promise.all(c.map(cat => api_getMapping(cat.id)));
      c.forEach((cat, i) => {
        if (results[i]) ms[cat.id] = results[i]!;
      });
      setMappings(ms);
    } catch {
      message.error('Failed to load categories');
    }
    setLoading(false);
  }, [sourceId]);

  useEffect(() => { load(); }, [load]);

  const dimOptions = (dim: string) =>
    dimVals
      .filter(d => d.dimension === dim)
      .map(d => ({ value: d.value_name, label: d.value_name }));

  const vulnOptions = dimVals
    .filter(d => d.dimension === 'vuln')
    .map(d => ({ value: d.value_name, label: d.value_name }));

  const confOptions = [
    { value: 'high', label: 'High' },
    { value: 'medium', label: 'Medium' },
    { value: 'low', label: 'Low' },
  ];

  const updateDim = async (catId: number, field: string, value: unknown) => {
    try {
      const m = mappings[catId] || {
        id: 0,
        category_id: catId,
        vuln_tags: [],
      };
      await api_updateMapping(catId, { [field]: value });
      setMappings(prev => ({
        ...prev,
        [catId]: { ...(prev[catId] || { id: 0, category_id: catId, vuln_tags: [] }), [field]: value },
      }));
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to update';
      message.error(msg);
    }
  };

  const handleCreate = async () => {
    try {
      const vals = await form.validateFields();
      await api_createCategory(sourceId, {
        original_name: vals.original_name,
        description: vals.description,
        is_threat: vals.is_threat,
      });
      message.success('Category added');
      setOpen(false);
      form.resetFields();
      load();
    } catch {
      // form validation or API error
    }
  };

  const handleDelete = async (catId: number) => {
    await api_deleteCategory(catId);
    message.success('Deleted');
    load();
  };

  const updateName = async (catId: number, value: string) => {
    await api_updateCategory(catId, { original_name: value });
    setCats(prev => prev.map(c => c.id === catId ? { ...c, original_name: value } : c));
  };

  const columns = [
    { title: 'ID', dataIndex: 'id', width: 60 },
    {
      title: 'Category Name',
      dataIndex: 'original_name',
      width: 280,
      render: (name: string, r: Category) => (
        <div>
          <Input size="small" defaultValue={name} style={{ border: 'none', background: 'transparent' }}
            onBlur={(e) => { if (e.target.value !== name) updateName(r.id, e.target.value); }}
            onPressEnter={(e: any) => { (e.target as HTMLInputElement).blur(); }} />
          {r.description ? (
            <div style={{ fontSize: 12, color: '#888', marginTop: 2, lineHeight: 1.4 }}>{r.description}</div>
          ) : null}
        </div>
      ),
    },
    {
      title: 'Threat',
      dataIndex: 'is_threat',
      width: 80,
      render: (v: boolean) =>
        v ? <Tag color="red">Yes</Tag> : <Tag>No</Tag>,
    },
    {
      title: 'Source Dim',
      width: 200,
      render: (_: unknown, r: Category) => (
        <Select
          mode="multiple"
          size="small"
          value={mappings[r.id]?.source_dim || undefined}
          onChange={(v: string[]) => updateDim(r.id, 'source_dim', v.length ? v : null)}
          options={dimOptions('source')}
          allowClear
          style={{ width: 190 }}
          placeholder="Select..."
        />
      ),
    },
    {
      title: 'Mech Dim',
      width: 200,
      render: (_: unknown, r: Category) => (
        <Select
          mode="multiple"
          size="small"
          value={mappings[r.id]?.mech_dim || undefined}
          onChange={(v: string[]) => updateDim(r.id, 'mech_dim', v.length ? v : null)}
          options={dimOptions('mech')}
          allowClear
          style={{ width: 190 }}
          placeholder="Select..."
        />
      ),
    },
    {
      title: 'Target Dim',
      width: 200,
      render: (_: unknown, r: Category) => (
        <Select
          mode="multiple"
          size="small"
          value={mappings[r.id]?.target_dim || undefined}
          onChange={(v: string[]) => updateDim(r.id, 'target_dim', v.length ? v : null)}
          options={dimOptions('target')}
          allowClear
          style={{ width: 190 }}
          placeholder="Select..."
        />
      ),
    },
    {
      title: 'Vuln Tags',
      width: 220,
      render: (_: unknown, r: Category) => (
        <Select
          mode="multiple"
          size="small"
          value={mappings[r.id]?.vuln_tags || []}
          onChange={(v: string[]) =>
            updateDim(r.id, 'vuln_tags', v.length ? v : null)
          }
          options={vulnOptions}
          style={{ width: 210 }}
          placeholder="Tags..."
          allowClear
        />
      ),
    },
    {
      title: 'Confidence',
      width: 110,
      render: (_: unknown, r: Category) => (
        <Select
          size="small"
          value={mappings[r.id]?.confidence || undefined}
          onChange={(v: string) => updateDim(r.id, 'confidence', v || null)}
          options={confOptions}
          allowClear
          style={{ width: 100 }}
          placeholder="?"
        />
      ),
    },
    {
      title: 'Status',
      dataIndex: 'status',
      width: 120,
      render: (s: string) => {
        const color = s === 'mapped' ? 'green' : s === 'needs_discussion' ? 'orange' : 'default';
        return <Tag color={color}>{s}</Tag>;
      },
    },
    {
      title: '',
      width: 50,
      render: (_: unknown, r: Category) => (
        <Button type="text" danger size="small" icon={<DeleteOutlined />}
          onClick={() => handleDelete(r.id)} />
      ),
    },
  ];

  return (
    <>
      <Breadcrumb
        style={{ marginBottom: 12 }}
        items={[
          { title: <a onClick={() => navigate('/sources')}>Sources</a> },
          { title: `Source #${sourceId}` },
        ]}
      />
      <Space style={{ marginBottom: 16 }}>
        <Button icon={<ArrowLeftOutlined />} onClick={() => navigate('/sources')}>
          Back to Sources
        </Button>
        <Button type="primary" icon={<PlusOutlined />} onClick={() => setOpen(true)}>
          Add Category
        </Button>
      </Space>
      <Table
        dataSource={cats}
        rowKey="id"
        columns={columns}
        loading={loading}
        size="small"
        pagination={{ pageSize: 50 }}
        scroll={{ x: 1200 }}
      />
      <Modal
        title="Add Category"
        open={open}
        onOk={handleCreate}
        onCancel={() => {
          setOpen(false);
          form.resetFields();
        }}
      >
        <Form form={form} layout="vertical">
          <Form.Item
            name="original_name"
            label="Category Name"
            rules={[{ required: true, message: 'Name is required' }]}
          >
            <Input />
          </Form.Item>
          <Form.Item name="description" label="Description">
            <Input.TextArea rows={3} />
          </Form.Item>
          <Form.Item name="is_threat" label="Is Threat" initialValue={true}>
            <Select
              options={[
                { value: true, label: 'Yes (Threat)' },
                { value: false, label: 'No (Benign)' },
              ]}
            />
          </Form.Item>
        </Form>
      </Modal>
    </>
  );
}
