import { useEffect, useState } from 'react';
import {
  Table,
  Button,
  Modal,
  Form,
  Input,
  Select,
  message,
  Tag,
  Popconfirm,
  Typography,
} from 'antd';
import { PlusOutlined } from '@ant-design/icons';
import {
  DimValue,
  api_getDimValues,
  api_createDimValue,
  api_updateDimValue,
  api_deleteDimValue,
} from '../api';

const { Title } = Typography;

const dimColors: Record<string, string> = {
  source: '#7170ff',
  mech: '#ff7c43',
  target: '#00bcd4',
  vuln: '#ff4d4f',
};

const dimLabels: Record<string, string> = {
  source: 'Source',
  mech: 'Mechanism',
  target: 'Target',
  vuln: 'Vulnerability',
};

export default function DimValuesPage() {
  const [dimVals, setDimVals] = useState<DimValue[]>([]);
  const [loading, setLoading] = useState(false);
  const [open, setOpen] = useState(false);
  const [editing, setEditing] = useState<DimValue | null>(null);
  const [form] = Form.useForm();

  const load = async () => {
    setLoading(true);
    try {
      const d = await api_getDimValues();
      setDimVals(d);
    } catch {
      message.error('Failed to load dimension values');
    }
    setLoading(false);
  };

  useEffect(() => {
    load();
  }, []);

  const handleSubmit = async () => {
    try {
      const vals = await form.validateFields();
      if (editing) {
        await api_updateDimValue(editing.id, vals);
        message.success('Dimension value updated');
      } else {
        await api_createDimValue(vals);
        message.success('Dimension value created');
      }
      setOpen(false);
      setEditing(null);
      form.resetFields();
      load();
    } catch {
      // validation error
    }
  };

  const handleEdit = (record: DimValue) => {
    setEditing(record);
    form.setFieldsValue(record);
    setOpen(true);
  };

  const handleDelete = async (id: number) => {
    try {
      await api_deleteDimValue(id);
      message.success('Deleted');
      load();
    } catch {
      message.error('Failed to delete');
    }
  };

  const openAdd = () => {
    setEditing(null);
    form.resetFields();
    setOpen(true);
  };

  const columns = [
    {
      title: 'Dimension',
      dataIndex: 'dimension',
      key: 'dimension',
      width: 120,
      render: (d: string) => (
        <Tag color={dimColors[d] || 'default'}>{dimLabels[d] || d}</Tag>
      ),
      filters: Object.entries(dimLabels).map(([value, text]) => ({
        text,
        value,
      })),
      onFilter: (value: unknown, record: DimValue) =>
        record.dimension === (value as string),
    },
    {
      title: 'Value Name',
      dataIndex: 'value_name',
      key: 'value_name',
      ellipsis: true,
    },
    {
      title: 'Definition',
      dataIndex: 'definition',
      key: 'definition',
      ellipsis: true,
      render: (d: string | null) => d || '-',
    },
    {
      title: 'Examples',
      dataIndex: 'examples',
      key: 'examples',
      ellipsis: true,
      width: 200,
      render: (d: string | null) => d || '-',
    },
    {
      title: 'Counter Examples',
      dataIndex: 'counter_examples',
      key: 'counter_examples',
      ellipsis: true,
      width: 200,
      render: (d: string | null) => d || '-',
    },
    {
      title: 'Actions',
      key: 'actions',
      width: 140,
      render: (_: unknown, record: DimValue) => (
        <Button.Group>
          <Button size="small" onClick={() => handleEdit(record)}>
            Edit
          </Button>
          <Popconfirm
            title="Delete this dimension value?"
            onConfirm={() => handleDelete(record.id)}
            okText="Yes"
            cancelText="No"
          >
            <Button size="small" danger>
              Del
            </Button>
          </Popconfirm>
        </Button.Group>
      ),
    },
  ];

  return (
    <div>
      <Title level={3}>Dimension Values</Title>

      <Button
        type="primary"
        icon={<PlusOutlined />}
        onClick={openAdd}
        style={{ marginBottom: 16 }}
      >
        Add Dimension Value
      </Button>

      <Table
        dataSource={dimVals}
        rowKey="id"
        columns={columns}
        loading={loading}
        size="small"
        pagination={{ pageSize: 50 }}
        expandable={{
          expandedRowRender: (record: DimValue) => (
            <div style={{ padding: '8px 24px' }}>
              {record.literature_ref && (
                <p>
                  <strong>Literature Reference:</strong> {record.literature_ref}
                </p>
              )}
              {record.decision_rules && (
                <p>
                  <strong>Decision Rules:</strong> {record.decision_rules}
                </p>
              )}
            </div>
          ),
          rowExpandable: (record: DimValue) =>
            !!(record.literature_ref || record.decision_rules),
        }}
      />

      <Modal
        title={editing ? 'Edit Dimension Value' : 'Add Dimension Value'}
        open={open}
        onOk={handleSubmit}
        onCancel={() => {
          setOpen(false);
          setEditing(null);
          form.resetFields();
        }}
        width={640}
      >
        <Form form={form} layout="vertical">
          <Form.Item
            name="dimension"
            label="Dimension"
            rules={[{ required: true, message: 'Dimension is required' }]}
          >
            <Select
              options={Object.entries(dimLabels).map(([value, label]) => ({
                value,
                label,
              }))}
            />
          </Form.Item>
          <Form.Item
            name="value_name"
            label="Value Name"
            rules={[{ required: true, message: 'Value name is required' }]}
          >
            <Input />
          </Form.Item>
          <Form.Item name="definition" label="Definition">
            <Input.TextArea rows={3} />
          </Form.Item>
          <Form.Item name="examples" label="Examples">
            <Input.TextArea rows={2} />
          </Form.Item>
          <Form.Item name="counter_examples" label="Counter Examples">
            <Input.TextArea rows={2} />
          </Form.Item>
          <Form.Item name="decision_rules" label="Decision Rules">
            <Input.TextArea rows={2} />
          </Form.Item>
          <Form.Item name="literature_ref" label="Literature Reference">
            <Input.TextArea rows={2} />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
}
