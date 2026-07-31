import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import { ProLayout } from '@ant-design/pro-layout';
import { BarChartOutlined, DatabaseOutlined, TagOutlined } from '@ant-design/icons';

export default function Layout() {
  const nav = useNavigate();
  const loc = useLocation();

  const menuData = [
    { path: '/', name: 'Dashboard', icon: <BarChartOutlined /> },
    { path: '/sources', name: 'Sources', icon: <DatabaseOutlined /> },
  ];

  return (
    <ProLayout
      title="Mapping DB"
      logo={null}
      location={loc}
      route={{ routes: menuData }}
      menuDataRender={() => menuData}
      menuItemRender={(item: { path?: string; name?: string; icon?: React.ReactNode }, dom: React.ReactNode) => (
        <div onClick={() => nav(item.path!)} style={{ cursor: 'pointer' }}>
          {dom}
        </div>
      )}
      fixSiderbar
      layout="mix"
      splitMenus={false}
      contentStyle={{ padding: 24, minHeight: '100vh' }}
    >
      <Outlet />
    </ProLayout>
  );
}
