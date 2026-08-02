import { useEffect, useState } from 'react';
import {
  Card,
  Col,
  Row,
  Statistic,
  Table,
  Spin,
  Typography,
  message,
} from 'antd';
import {
  DatabaseOutlined,
  TagsOutlined,
  CheckCircleOutlined,
  AlertOutlined,
} from '@ant-design/icons';
import ReactEChartsCore from 'echarts-for-react/lib/core';
import * as echarts from 'echarts/core';
import { BarChart, PieChart, SankeyChart } from 'echarts/charts';
import {
  GridComponent,
  TooltipComponent,
  TitleComponent,
  LegendComponent,
} from 'echarts/components';
import { CanvasRenderer } from 'echarts/renderers';
import {
  Stats,
  Source,
  Category,
  Mapping,
  api_getStats,
  api_getSources,
  api_getCategories,
  api_getMapping,
} from '../api';

// Register ECharts components
echarts.use([
  BarChart,
  PieChart,
  SankeyChart,
  GridComponent,
  TooltipComponent,
  TitleComponent,
  LegendComponent,
  CanvasRenderer,
]);

const { Title } = Typography;

interface SankeyNode {
  name: string;
}

interface SankeyLink {
  source: string;
  target: string;
  value: number;
}

export default function DashboardPage() {
  const [stats, setStats] = useState<Stats | null>(null);
  const [sankeyData, setSankeyData] = useState<{
    nodes: SankeyNode[];
    links: SankeyLink[];
  }>({ nodes: [], links: [] });
  const [loading, setLoading] = useState(true);
  const [sankeyLoading, setSankeyLoading] = useState(true);

  useEffect(() => {
    const loadStats = async () => {
      try {
        const s = await api_getStats();
        setStats(s);
      } catch {
        message.error('Failed to load stats');
      }
      setLoading(false);
    };
    loadStats();
  }, []);

  useEffect(() => {
    const loadSankey = async () => {
      try {
        // Fetch all mappings by getting all sources → categories → mappings
        const sources = await api_getSources();
        const categoryBatches = await Promise.all(
          sources.map((s: Source) => api_getCategories(s.id))
        );
        const allCats: Category[] = categoryBatches.flat();

        const mappingResults = await Promise.all(
          allCats.map((c: Category) => api_getMapping(c.id))
        );
        const allMappings: Mapping[] = mappingResults.filter(
          (m): m is Mapping => m !== null
        );

        // Build Sankey: source_dim → mech_dim → target_dim
        // Multi-valued dims expand to element-wise edges (each value is its own node)
        const transitionCounts = new Map<string, number>();
        const nodeSet = new Set<string>();

        for (const m of allMappings) {
          const sources = m.source_dim || [];
          const mechs = m.mech_dim || [];
          const targets = m.target_dim || [];
          for (const s of sources) {
            for (const me of mechs) {
              const key = `S→M:${s}→${me}`;
              transitionCounts.set(key, (transitionCounts.get(key) || 0) + 1);
              nodeSet.add(s);
              nodeSet.add(me);
            }
          }
          for (const me of mechs) {
            for (const t of targets) {
              const key = `M→T:${me}→${t}`;
              transitionCounts.set(key, (transitionCounts.get(key) || 0) + 1);
              nodeSet.add(me);
              nodeSet.add(t);
            }
          }
        }

        const nodes: SankeyNode[] = Array.from(nodeSet).map(name => ({
          name,
        }));

        const links: SankeyLink[] = [];
        for (const [key, value] of transitionCounts) {
          const [, pair] = key.split(':');
          const [source, target] = pair.split('→');
          links.push({ source, target, value });
        }

        setSankeyData({ nodes, links });
      } catch {
        message.error('Failed to load Sankey data');
      }
      setSankeyLoading(false);
    };
    loadSankey();
  }, []);

  if (loading) {
    return (
      <div style={{ textAlign: 'center', paddingTop: 100 }}>
        <Spin size="large" />
      </div>
    );
  }

  if (!stats) {
    return <div>No data available</div>;
  }

  const barOption = (data: Record<string, number>, name: string) => ({
    tooltip: { trigger: 'axis' },
    grid: { left: 100, right: 30, top: 20, bottom: 40 },
    xAxis: {
      type: 'value',
    },
    yAxis: {
      type: 'category',
      data: Object.keys(data),
      axisLabel: { width: 90, overflow: 'truncate' },
    },
    series: [
      {
        name,
        type: 'bar',
        data: Object.values(data),
        itemStyle: {
          color:
            name === 'Source'
              ? '#7170ff'
              : name === 'Mechanism'
                ? '#ff7c43'
                : '#00bcd4',
        },
      },
    ],
  });

  const sankeyOption = {
    tooltip: { trigger: 'item', triggerOn: 'mousemove' },
    series: [
      {
        type: 'sankey',
        layout: 'none',
        emphasis: { focus: 'adjacency' },
        nodeAlign: 'left',
        layoutIterations: 0,
        data: sankeyData.nodes,
        links: sankeyData.links,
        label: { show: true, fontSize: 11 },
        lineStyle: { color: 'gradient', curveness: 0.5 },
      },
    ],
  };

  const pieOption = {
    tooltip: { trigger: 'item' },
    legend: { orient: 'vertical', left: 'left' },
    series: [
      {
        name: 'Confidence',
        type: 'pie',
        radius: ['40%', '70%'],
        data: Object.entries(stats.confidence_distribution).map(([name, value]) => ({
          name,
          value,
        })),
        itemStyle: {
          color: (params: { name: string }) =>
            params.name === 'high'
              ? '#52c41a'
              : params.name === 'medium'
                ? '#faad14'
                : '#ff4d4f',
        },
        label: { formatter: '{b}: {c} ({d}%)' },
      },
    ],
  };

  const sourceColumns = [
    { title: 'Source', dataIndex: 'name', key: 'name' },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      width: 120,
    },
    {
      title: 'Categories',
      dataIndex: 'cats',
      key: 'cats',
      width: 110,
    },
    {
      title: 'Mapped',
      dataIndex: 'mapped',
      key: 'mapped',
      width: 100,
    },
    {
      title: 'Progress',
      key: 'progress',
      width: 160,
      render: (_: unknown, r: SourceBreakdown) => {
        const pct = r.cats > 0 ? Math.round((r.mapped / r.cats) * 100) : 0;
        return <span>{pct}% ({r.mapped}/{r.cats})</span>;
      },
    },
  ];

  interface SourceBreakdown {
    id: number;
    name: string;
    status: string;
    cats: number;
    mapped: number;
  }

  return (
    <div>
      <Title level={3}>Dashboard</Title>

      {/* Stat Cards */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={6}>
          <Card>
            <Statistic
              title="Sources"
              value={stats.total_sources}
              prefix={<DatabaseOutlined />}
              valueStyle={{ color: '#7170ff' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="Categories"
              value={stats.total_categories}
              prefix={<TagsOutlined />}
              valueStyle={{ color: '#ff7c43' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="Mapped"
              value={stats.total_mapped}
              prefix={<CheckCircleOutlined />}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="Threats"
              value={stats.total_threats}
              prefix={<AlertOutlined />}
              valueStyle={{ color: '#ff4d4f' }}
            />
          </Card>
        </Col>
      </Row>

      {/* Bar Charts Row */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={8}>
          <Card title="Source Dimension Distribution">
            <ReactEChartsCore
              echarts={echarts}
              option={barOption(stats.dim_source_distribution, 'Source')}
              style={{ height: 300 }}
            />
          </Card>
        </Col>
        <Col span={8}>
          <Card title="Mechanism Dimension Distribution">
            <ReactEChartsCore
              echarts={echarts}
              option={barOption(stats.dim_mech_distribution, 'Mechanism')}
              style={{ height: 300 }}
            />
          </Card>
        </Col>
        <Col span={8}>
          <Card title="Target Dimension Distribution">
            <ReactEChartsCore
              echarts={echarts}
              option={barOption(stats.dim_target_distribution, 'Target')}
              style={{ height: 300 }}
            />
          </Card>
        </Col>
      </Row>

      {/* Sankey + Pie Row */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={16}>
          <Card title="Attack Flow (Source → Mechanism → Target)">
            {sankeyLoading ? (
              <div style={{ textAlign: 'center', padding: 50 }}>
                <Spin />
              </div>
            ) : sankeyData.links.length === 0 ? (
              <div style={{ textAlign: 'center', padding: 50, color: '#999' }}>
                No mapping data yet. Map some categories to see the Sankey diagram.
              </div>
            ) : (
              <ReactEChartsCore
                echarts={echarts}
                option={sankeyOption}
                style={{ height: 400 }}
              />
            )}
          </Card>
        </Col>
        <Col span={8}>
          <Card title="Confidence Distribution">
            <ReactEChartsCore
              echarts={echarts}
              option={pieOption}
              style={{ height: 400 }}
            />
          </Card>
        </Col>
      </Row>

      {/* Source Progress Table */}
      <Card title="Source Progress">
        <Table
          dataSource={stats.source_breakdown}
          rowKey="id"
          columns={sourceColumns}
          pagination={{ pageSize: 15 }}
          size="small"
        />
      </Card>
    </div>
  );
}
