"""Seed the dimension_values table with canonical values on first run."""

from app.database import get_pool

DIMENSION_VALUES = [
    # (dimension, value_name, definition, examples, counter_examples, decision_rules, literature_ref)
    ("source", "供应链", "恶意来自第三方依赖、仓库、包管理器的构建/分发环节", "Supply Chain 类（第三方依赖、仓库投毒）、SC1 未固定依赖、内嵌恶意脚本的 SKILL.md", "用户直接粘贴的注入文本=用户输入；运行时抓取的网页=外部不可信内容", "恶意内容随 skill/插件/依赖安装时进入，安装即存在", "MAPPING_SPEC V1；Unit 42 BIV 供应链分析"),
    ("source", "用户输入", "恶意指令直接来自用户写的 prompt、对话、上传的文件", "用户粘贴注入文本、诱导性指令、上传的恶意文件", "skill 自带指令=供应链；网页内容=外部不可信内容", "恶意内容来自直接使用者的输入（prompt/对话/文件）", "MAPPING_SPEC V1；OWASP LLM01 直接注入"),
    ("source", "外部不可信内容", "恶意藏在 URL、网页、引用的外部数据中", "被投毒的网页、邮件、RAG 文档、API 响应（间接注入）", "用户主动粘贴=用户输入", "恶意内容在 agent 运行时从外部源读取", "Greshake et al. arXiv:2302.12173；OWASP LLM01 间接注入"),
    ("source", "运行时环境", "恶意来自 MCP server、其他 agent、系统进程", "恶意 MCP server、其他 agent、工具描述投毒", "prompt 本身不是来源——它是通道", "恶意来自运行时环境中的其他组件（非用户、非外部数据）", "MAPPING_SPEC V1；OWASP LLM06 multi-agent"),
    ("source", "来源不明", "原始分类未陈述攻击从哪个渠道进入", "SkillSpector P1 指令覆盖（未述通道）、E1 外部传输（未述通道）", "原文明确提到通道时不能标不明", "读了原文、确实未陈述进入渠道才标；不替扫描器编造", "映射基线 2026-08-02：宁标不明不硬猜"),
    ("mech", "指令操纵", "以自然语言/文本为载体，作用于模型的理解与决策层，使模型做出本不会做的选择或输出", "P1 指令覆盖（ignore previous instructions）、P5 有害内容指令、越狱、tool 描述投毒", "文本驱动结果为执行代码（curl|bash）=代码执行；藏匿文本=叠加混淆；P3 外泄命令是文本载体+执行动作的复合", "载体是文本 + 生效对象是模型语义决策；若生效的是进程/代码执行则归代码执行", "OWASP LLM01:2025；arXiv:2601.10338；MITRE ATLAS AML.T0051"),
    ("mech", "混淆隐藏", "可叠加属性（不参与主值互斥判定）：通过隐藏/混淆规避检测（base64、Unicode、同形异义符、藏注释）", "P2 隐藏指令（注释/不可见文本）、base64 编码载荷、同形异义符冒充", "不是独立攻击动作，需叠加在主方式上（藏指令/藏代码/藏下载）", "原文同时陈述隐藏手段与攻击动作时，作为附加属性叠加", "MITRE ATT&CK T1027 Obfuscated Files"),
    ("mech", "状态污染", "memory poisoning、修改 system prompt、上下文状态篡改", "P4 行为操纵（always/never/every 持续行为改变）、Memory Poisoning、自修改、持久化后门", "一次性执行后退出；通过指令改变单次输出（那是指令操纵）", "攻击污染持久状态或长期行为模式（记忆/配置/进程驻留）", "CWE-653 关联；arXiv:2603.11619（Taming OpenClaw）memory poisoning"),
    ("mech", "方式不明", "原始分类未陈述具体攻击手段", "原文只描述后果未述手段的分类（如纯目标导向类别）", "原文明确提到 exec/指令/权限时不能标不明", "读了原文、确实未陈述技术手段才标", "映射基线 2026-08-02"),
    ("mech", "代码执行", "直接执行恶意代码/命令——exec/eval/subprocess、命令注入、RCE；扫描器检测锚点", "AST1-9 exec/eval/subprocess、E1 外部传输、curl|bash", "通过指令诱导 agent 执行=指令操纵", "检测到代码级执行动作（进程/命令/脚本运行）而非文本驱动", "CWE-94/77；MITRE ATT&CK T1059"),
    ("mech", "权限滥用", "滥用超出所需的权限/能力——权限提升、权限请求、越权调用工具", "PE1 权限请求（request full access）、PE2 sudo/root 提权、LP2 通配符权限、越权调用危险工具", "权限声明正确但被注入利用=缺乏输入验证；合理权限下调用工具", "攻击者主动请求/获取/使用超出声明的权限或能力", "OWASP LLM06:2025 Excessive Agency；CWE-732/250"),
    ("mech", "依赖操纵", "利用依赖/包管理机制——投毒未锁定依赖、exploit 已知漏洞依赖、拼写劫持、远程下载依赖", "SC1 未锁定依赖、SC4 已知CVE依赖、SC5 废弃包、SC6 拼写劫持、SC2 curl|bash（与代码执行复合）", "直接执行代码=代码执行（SC2 复合）；经文本指令=指令操纵", "攻击通过依赖/包/仓库机制实施或依赖本身有可被利用的漏洞", "CWE-829/494/347；OWASP LLM03:2025"),
    ("mech", "触发机制滥用", "利用/滥用的激活机制——skill 的触发器（triggers 元数据）被设计成有害形态：过宽触发扩大攻击面、影子命令冒充系统命令、关键词诱饵最大化激活", "TR1 过宽触发（常见词/短词）、TR2 影子命令（触发词=ls/cd 等内置命令）、TR3 关键词诱饵（anything/everything/all messages）", "代码级执行=代码执行；指令驱动模型=指令操纵；权限范围过大=权限滥用", "攻击面/激活机制被设计成有害（SKILL.md triggers 字段）", "SkillSpector Trigger Abuse 类；ASI 框架；agent skill 生态特有（论文贡献点候选）"),
    ("target", "窃取信息", "违反机密性——读取/外传敏感数据、环境变量、系统提示", "数据外泄、凭证窃取、系统提示泄露、上下文外传（E1-E4）", "仅读取非敏感配置信息", "攻击者拿到了敏感数据（机密性违反）", "CIA 机密性；OWASP LLM02/LLM07"),
    ("target", "破坏系统", "违反完整性和可用性——加密勒索、删除数据、植入后门", "删改文件、篡改配置、勒索、破坏功能", "只是把数据偷走（那=窃取信息）", "攻击损害系统/数据完整性或可用性", "CIA 完整性/可用性"),
    ("target", "持久控制", "违反控制性——写 cron、改配置、创建进程驻留", "写 cron、改配置、创建进程驻留、Rogue Agent 持久化", "一次性执行后退出（无持久证据不标）", "必须有明确持久化证据（写文件/改配置/创建进程）", "MITRE ATT&CK TA0003 Persistence"),
    ("target", "绕过防御", "反检测、反拒绝、混淆意图以逃避安全策略", "AR1-3 抗拒绝、反检测、绕过审核、隐藏行为", "直接攻击系统（不涉及防御机制）", "针对安全机制/对齐/审计的对抗", "MITRE ATT&CK TA0005 Defense Evasion"),
    ("target", "资源滥用", "间接违反可用性——盗用计算资源、API quota 挖矿", "挖矿、DoS、API quota 耗尽、额度/金钱耗尽", "正常功能调用", "滥用计算/API/资金资源（可用性间接违反）", "OWASP LLM10 Unbounded Consumption；CWE-400/770"),
    ("target", "目标不明", "原始分类未陈述攻击的最终后果", "只描述机制未述后果的分类（如 P2 隐藏指令）", "原文明确后果（外传/破坏）时不标", "读了原文、确实未陈述攻击后果才标", "映射基线 2026-08-02"),
    ("target", "内容安全危害", "违反内容安全——模型输出可致物理伤害/违法/自残等有害内容，受害对象是工具用户（人）", "P5 有害内容（投毒食谱/爆炸物/自残指令）", "危害的是系统本身=破坏系统", "后果是现实世界危害、受害对象是人而非系统", "OWASP LLM09:2025 Misinformation；SkillSpector P5"),
    ("vuln", "缺乏输入验证与信任隔离", "系统未验证输入来源和可信度就纳入执行上下文；未区分指令与数据（数据-指令边界缺失）", "Prompt Injection（直接/间接）、P1 指令覆盖、AR 抗拒绝", "依赖未锁定=供应链问题；权限过宽=授权问题", "攻击成功的关键是系统无差别信任输入/未区分指令与数据", "CWE-77/94/74（CWE-20 已弃用）；OWASP LLM01；arXiv:2604.02837 数据-指令边界"),
    ("vuln", "供应链完整性缺失", "依赖版本未固定、未验证来源完整性与出处；包内内容被篡改（字节码/依赖替换）", "SC1 未固定依赖、SC2 curl|bash、typosquatting、已知 CVE 依赖、字节码篡改(.pyc vs .py 不符)、依赖替换、隐藏文件藏代码", "已锁定版本+校验和的正常依赖", "分类提到未锁定版本/CVE/可疑 URL/未验证完整性/字节码篡改/依赖替换", "CWE-829/494/347；OWASP LLM03"),
    ("vuln", "权限过宽（最小权限违反）", "工具授权范围远超实际需要，违反最小权限原则（原：权限过宽（通配符））", "MCP 通配符权限、LP2、PE1 权限请求、EA 过度授权", "合理的最小权限分配", "分类提到通配符/过度权限/越权/未限制范围", "CWE-732/250；OWASP LLM06"),
    ("vuln", "缺乏输出过滤", "未对模型/工具输出做安全过滤和消毒", "OH1 未验证输出注入、LLM 输出直入 shell/浏览器、P5 有害输出未过滤", "信息泄露（输出文本未达危险 sink）", "攻击成功因输出未经编码/消毒/验证就传给下游", "CWE-116/79；OWASP LLM05"),
    ("vuln", "状态未隔离", "用户或会话间的状态未隔离导致交叉污染", "共享记忆被投毒影响后续会话、跨用户状态污染", "单会话内一次性攻击", "状态跨用户/会话/信任边界共享且未隔离", "CWE-653；arXiv:2604.02837 单次批准模型"),
    ("vuln", "未声明能力与实际不符", "skill 声明的功能与实际行为不一致", "声称只读实际外联（E1）、描述-行为不匹配（TP4）、隐藏能力", "用户没读声明（用户侧问题）；bug 导致的意外行为", "实际运行时行为与声明/元数据不符且用户依赖声明授信", "Unit 42 BIV；Liu 2026a undocumented capabilities"),
    ("vuln", "过度自主/缺人机确认", "高影响操作无人工确认门，单次批准后长期有效（OWASP LLM06）", "EA2 自主决策无 HITL、单次批准后长期有效", "权限过宽但动作仍需确认（那=权限过宽）", "高影响操作缺人工确认门", "OWASP LLM06 excessive autonomy；arXiv:2604.02837"),
    ("vuln", "工具调用缺乏约束", "工具/命令调用缺少安全控制层——危险参数未校验、无 deny 列表、无 hook 拦截、校验可被跳过", "TM1 shell=True/rm -rf、TM2 链式绕过单点检查、TM3 verify=False/auth=None", "授权范围过大=权限过宽（EA1）；输入未验证=缺乏输入验证", "攻击成功因工具调用无危险参数校验/无 deny 列表/无 hook/默认关校验", "CWE-1188 Insecure Defaults；CWE-250；OWASP LLM05；mapping-v1 GAP（缺 deny 列表/缺 hook）"),
    ("vuln", "状态/代码完整性保护缺失", "系统允许持久状态（记忆/上下文）或自身代码/配置在运行时被篡改——无完整性校验、无不可变保护、无防篡改机制", "RA1 自修改（open(__file__,'w')/write to SKILL.md）、RA2 写 crontab/.bashrc、MP1 记忆持久注入、MP3 记忆篡改", "跨用户/会话状态污染=状态未隔离（CWE-653）；仅读取状态无篡改=不适用", "攻击成功因持久状态/自身代码可被运行时写入或改写且无校验", "CWE-353（完整性校验缺失）；MITRE ATLAS AML.T0080（记忆投毒）；ASI10"),
    ("vuln", "触发条件设计缺陷", "skill 的激活条件（triggers 元数据）设计有害——过宽触发扩大攻击面、影子命令冒充系统命令欺骗用户、关键词诱饵匹配几乎所有输入", "TR1 过宽（常见词激活）、TR2 影子命令（触发词=内置命令）、TR3 诱饵（匹配一切输入）", "功能声明与实际行为不符=未声明能力与实际不符（TP4）；权限范围过大=权限过宽", "攻击成功/攻击面扩大因激活条件设计有害——元数据层面非代码/指令/权限", "SkillSpector Trigger Abuse；agent skill 生态特有（论文贡献点候选）"),
    ("vuln", "代码执行能力过宽", "skill 代码被允许调用任意执行原语（exec/eval/subprocess/os.system/compile/getattr 反射）且无沙箱、无最小能力约束——最小能力原则在代码层的违反", "AST1 exec()、AST2 eval()、AST4 subprocess、AST5 os.system、AST8 exec(网络数据)、AST9 getattr(os, system)", "授权/权限范围过大=权限过宽（PE1/EA1）；工具调用参数无校验=工具调用缺乏约束（TM1-3）；仅调用系统工具无执行原语=不适用", "代码含任意代码执行原语且运行环境无限制——与权限过宽（授权面）区分：这是代码能力面", "CWE-250 Execution with Unnecessary Privileges；OWASP LLM06 Excessive Agency；最小权限原则（代码层）"),
    ("vuln", "数据流缺乏安全控制", "系统允许数据从源（凭证/文件/网络/用户输入）流向危险汇（网络出口/代码执行/文件写）且路径上无净化/无过滤/无隔离/无监控——数据流路径缺乏安全控制", "TT1 直接流（源→汇无净化）、TT3 凭证→网络、TT4 文件→网络、TT5 外部输入→exec、E1-E4 数据外泄", "仅读取敏感数据不外传=敏感信息泄露（结果面，非路径缺陷）；输入未验证来源=缺乏输入验证与信任隔离（源侧）", "攻击成功因数据在源→汇路径上无阻碍流动（无净化/过滤/隔离/监控）——路径侧缺陷，区别于源侧（输入验证）与结果侧（泄露）", "TT1 README 原文 without sanitization；OWASP LLM02 数据外泄；CWE-200 信息暴露（路径缺控制面）"),    ("vuln", "硬编码凭证无保护", "系统允许密钥/凭证以明文形式硬编码在代码或文档中且无保护——密钥管理缺陷", "Cisco SECRET_AWS_KEY(AKIA...)/SECRET_STRIPE_KEY(sk_live_...)/SECRET_GOOGLE_API(AIza...)/SECRET_GITHUB_TOKEN(ghp_...)/SECRET_PRIVATE_KEY(BEGIN RSA PRIVATE KEY)/SECRET_CONNECTION_STRING(mysql://user:pass@host)", "读取环境变量=好实践非漏洞(DATA_EXFIL_ENV_VARS 被 Cisco 移除)；密钥经数据流外传=数据流缺乏安全控制(TT3/4)", "攻击成功因密钥明文存在于代码/文档且无保护——静态暴露，非数据流路径问题", "CWE-798 Use of Hard-coded Credentials；GitHub secret scanning 同款"),

    ("carrier", "提示词", "攻击经文本/指令载体实施——注入、覆盖、越狱指令", "P1-P5 指令覆盖/隐藏/外泄（经文本实施）、tool 描述投毒", "直接执行代码（载体=代码）", "攻击数据/指令流经文本或模型输入通道", "载体定义 2026-08-02"),
    ("carrier", "代码", "攻击经代码载体实施——脚本、程序逻辑", "AST1-9 exec/eval/subprocess、PE2 sudo 命令、curl|bash", "纯文本指令（载体=提示词）", "攻击经代码/命令执行机制实施", "载体定义 2026-08-02"),
    ("carrier", "网络", "攻击经网络载体实施——数据外传、远程请求", "E1 外部传输、E4 上下文外传、SSRF", "本地文件读取（载体=文件）", "攻击数据流经网络通道", "载体定义 2026-08-02"),
    ("carrier", "文件", "攻击经文件系统载体实施——枚举、读取、写入敏感文件", "E3 文件枚举、PE3 读凭证文件、文件投毒", "读环境变量（载体=数据）", "攻击数据在文件系统", "载体定义 2026-08-02"),
    ("carrier", "数据", "攻击经数据载体实施——环境变量、配置、上下文中的敏感数据", "E2 环境变量收割、配置中的密钥", "文件系统中的文件（载体=文件）", "攻击数据来自 env/配置/上下文存储", "载体定义 2026-08-02"),
    ("carrier", "状态", "攻击经状态载体实施——记忆、会话、持久状态", "Memory Poisoning、跨会话状态污染", "一次性会话内攻击", "攻击数据在持久状态/记忆中", "载体定义 2026-08-02"),
    ("carrier", "依赖", "攻击经依赖载体实施——包、库、外部组件", "SC1 未锁定依赖、依赖混淆、typosquatting", "直接执行代码（载体=代码）", "攻击经依赖/包/外部组件实施", "载体定义 2026-08-02"),
    ("carrier", "载体不明", "原始分类未陈述攻击通过的媒介", "声明类攻击（PE1 请求权限）无数据流", "能判断数据流时不标", "原文未述或声明/配置类无数据流", "载体定义 2026-08-02"),
]


async def seed_dimension_values():
    """Insert canonical dimension values if the table is empty."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        existing = await conn.fetchval("SELECT COUNT(*) FROM dimension_values")
        if existing > 0:
            return  # already seeded

        for dim, name, definition, examples, counter_examples, decision_rules, literature_ref in DIMENSION_VALUES:
            await conn.execute(
                "INSERT INTO dimension_values (dimension, value_name, definition, examples, counter_examples, decision_rules, literature_ref) "
                "VALUES ($1, $2, $3, $4, $5, $6, $7) ON CONFLICT (dimension, value_name) DO NOTHING",
                dim, name, definition, examples, counter_examples, decision_rules, literature_ref,
            )
