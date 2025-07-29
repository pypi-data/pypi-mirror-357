"""tke基础接口封装。 注:自动生成"""
from lib.models import Model
from lib.utils import retry_with_conditions
from tencentcloud.tke.v20180525.tke_client import TkeClient as TkeClient_v20180525
from tencentcloud.tke.v20180525 import models as model_v20180525
from tencentcloud.tke.v20220501.tke_client import TkeClient as TkeClient_v20220501
from tencentcloud.tke.v20220501 import models as model_v20220501

    
class TkeBase(Model):
    def init_client_models(self, **kwargs):
        self.business = "tke"
        self.versions = ["2018-05-25", "2022-05-01"]
        self.client_v20180525 = TkeClient_v20180525(**kwargs)
        self.model_v20180525 = model_v20180525
        self.client_v20220501 = TkeClient_v20220501(**kwargs)
        self.model_v20220501 = model_v20220501

    @retry_with_conditions(3, 10)
    def acquire_cluster_admin_role(self, cluster_id=None, **kwargs):
        """通过此接口，可以获取集群的tke:admin的ClusterRole，即管理员角色，可以用于CAM侧高权限的用户，通过CAM策略给予子账户此接口权限，进而可以通过此接口直接获取到kubernetes集群内的管理员角色。
        :param cluster_id: 集群ID
        :type cluster_id: str
        
        """
        req = self.model_v20180525.AcquireClusterAdminRoleRequest()
        req.ClusterId = cluster_id
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.AcquireClusterAdminRole(req)
        return response

    @retry_with_conditions(3, 10)
    def add_cluster_cidr(self, cluster_id=None, cluster_cid_rs=None, ignore_cluster_cidr_conflict=None, **kwargs):
        """给GR集群增加可用的ClusterCIDR（开白才能使用此功能，如需要请联系我们）
        :param cluster_id: 集群ID
        :type cluster_id: str
        :param cluster_cid_rs: 增加的ClusterCIDR
        :type cluster_cid_rs: list of str
        :param ignore_cluster_cidr_conflict: 是否忽略ClusterCIDR与VPC路由表的冲突
        :type ignore_cluster_cidr_conflict: bool
        
        """
        req = self.model_v20180525.AddClusterCIDRRequest()
        req.ClusterId = cluster_id
        req.ClusterCIDRs = cluster_cid_rs
        req.IgnoreClusterCIDRConflict = ignore_cluster_cidr_conflict
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.AddClusterCIDR(req)
        return response

    @retry_with_conditions(3, 10)
    def add_existed_instances(self, cluster_id=None, instance_ids=None, instance_advanced_settings=None, enhanced_service=None, login_settings=None, host_name=None, security_group_ids=None, node_pool=None, skip_validate_options=None, instance_advanced_settings_overrides=None, image_id=None, **kwargs):
        """添加已经存在的实例到集群
        :param cluster_id: 集群ID
        :type cluster_id: str
        :param instance_ids: 实例列表，不支持竞价实例
        :type instance_ids: list of str
        :param instance_advanced_settings: 实例额外需要设置参数信息(默认值)
        :type instance_advanced_settings: :class:`tencentcloud.tke.v20180525.models.instance_advanced_settings`
        :param enhanced_service: 增强服务。通过该参数可以指定是否开启云安全、云监控等服务。若不指定该参数，则默认开启云监控、云安全服务。
        :type enhanced_service: :class:`tencentcloud.tke.v20180525.models.enhanced_service`
        :param login_settings: 节点登录信息（目前仅支持使用Password或者单个KeyIds）
        :type login_settings: :class:`tencentcloud.tke.v20180525.models.login_settings`
        :param host_name: 重装系统时，可以指定修改实例的host_name(集群为host_name模式时，此参数必传，规则名称除不支持大写字符外与[CVM创建实例](https://cloud.tencent.com/document/product/213/15730)接口host_name一致)
        :type host_name: str
        :param security_group_ids: 实例所属安全组。该参数可以通过调用 DescribeSecurityGroups 的返回值中的sgId字段来获取。若不指定该参数，则绑定默认安全组。（目前仅支持设置单个sgId）
        :type security_group_ids: list of str
        :param node_pool: 节点池选项
        :type node_pool: :class:`tencentcloud.tke.v20180525.models.node_poolOption`
        :param skip_validate_options: 校验规则相关选项，可配置跳过某些校验规则。目前支持GlobalRouteCIDRCheck（跳过GlobalRouter的相关校验），VpcCniCIDRCheck（跳过VpcCni相关校验）
        :type skip_validate_options: list of str
        :param instance_advanced_settingsOverrides: 参数instance_advanced_settingsOverride数组用于定制化地配置各台instance，与instance_ids顺序对应。当传入instance_advanced_settingsOverrides数组时，将覆盖默认参数instance_advanced_settings；当没有传入参数instance_advanced_settingsOverrides时，instance_advanced_settings参数对每台instance生效。参数instance_advanced_settingsOverride数组的长度应与instance_ids数组一致；当长度大于instance_ids数组长度时将报错；当长度小于instance_ids数组时，没有对应配置的instance将使用默认配置。
        :type instance_advanced_settingsOverrides: list of instance_advanced_settings
        :param image_id: 节点镜像
        :type image_id: str
        
        """
        req = self.model_v20180525.AddExistedInstancesRequest()
        req.ClusterId = cluster_id
        req.InstanceIds = instance_ids
        req.InstanceAdvancedSettings = instance_advanced_settings
        req.EnhancedService = enhanced_service
        req.LoginSettings = login_settings
        req.HostName = host_name
        req.SecurityGroupIds = security_group_ids
        req.NodePool = node_pool
        req.SkipValidateOptions = skip_validate_options
        req.InstanceAdvancedSettingsOverrides = instance_advanced_settings_overrides
        req.ImageId = image_id
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.AddExistedInstances(req)
        return response

    @retry_with_conditions(3, 10)
    def add_node_to_node_pool(self, cluster_id=None, node_pool_id=None, instance_ids=None, **kwargs):
        """将集群内节点移入节点池
        :param cluster_id: 集群id
        :type cluster_id: str
        :param node_pool_id: 节点池id
        :type node_pool_id: str
        :param instance_ids: 节点id
        :type instance_ids: list of str
        
        """
        req = self.model_v20180525.AddNodeToNodePoolRequest()
        req.ClusterId = cluster_id
        req.NodePoolId = node_pool_id
        req.InstanceIds = instance_ids
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.AddNodeToNodePool(req)
        return response

    @retry_with_conditions(3, 10)
    def add_vpc_cni_subnets(self, cluster_id=None, subnet_ids=None, vpc_id=None, skip_adding_non_masquerade_cid_rs=None, **kwargs):
        """针对VPC-CNI模式的集群，增加集群容器网络可使用的子网
        :param cluster_id: 集群ID
        :type cluster_id: str
        :param subnet_ids: 为集群容器网络增加的子网列表
        :type subnet_ids: list of str
        :param vpc_id: 集群所属的VPC的ID
        :type vpc_id: str
        :param skip_adding_non_masquerade_cid_rs: 是否同步添加 vpc 网段到 ip-masq-agent-config 的 NonMasqueradeCIDRs 字段，默认 false 会同步添加
        :type skip_adding_non_masquerade_cid_rs: bool
        
        """
        req = self.model_v20180525.AddVpcCniSubnetsRequest()
        req.ClusterId = cluster_id
        req.SubnetIds = subnet_ids
        req.VpcId = vpc_id
        req.SkipAddingNonMasqueradeCIDRs = skip_adding_non_masquerade_cid_rs
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.AddVpcCniSubnets(req)
        return response

    @retry_with_conditions(3, 10)
    def cancel_cluster_release(self, id=None, cluster_id=None, cluster_type=None, **kwargs):
        """在应用市场中取消安装失败的应用
        :param id: 应用id
        :type id: str
        :param cluster_id: 集群id
        :type cluster_id: str
        :param cluster_type: 集群类型
        :type cluster_type: str
        
        """
        req = self.model_v20180525.CancelClusterReleaseRequest()
        req.ID = id
        req.ClusterId = cluster_id
        req.ClusterType = cluster_type
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.CancelClusterRelease(req)
        return response

    @retry_with_conditions(3, 10)
    def check_edge_cluster_cidr(self, vpc_id=None, pod_cidr=None, service_cidr=None, **kwargs):
        """检查边缘计算集群的CIDR是否冲突
        :param vpc_id: 集群的vpc-id
        :type vpc_id: str
        :param pod_cidr: 集群的pod CIDR
        :type pod_cidr: str
        :param service_cidr: 集群的service CIDR
        :type service_cidr: str
        
        """
        req = self.model_v20180525.CheckEdgeClusterCIDRRequest()
        req.VpcId = vpc_id
        req.PodCIDR = pod_cidr
        req.ServiceCIDR = service_cidr
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.CheckEdgeClusterCIDR(req)
        return response

    @retry_with_conditions(3, 10)
    def check_instances_upgrade_able(self, cluster_id=None, instance_ids=None, upgrade_type=None, offset=None, limit=None, filter=None, **kwargs):
        """检查给定节点列表中哪些是可升级的
        :param cluster_id: 集群ID
        :type cluster_id: str
        :param instance_ids: 节点列表，空为全部节点
        :type instance_ids: list of str
        :param upgrade_type: 升级类型，枚举值：reset(重装升级，支持大版本和小版本)，hot(原地滚动小版本升级)，major(原地滚动大版本升级)
        :type upgrade_type: str
        :param offset: 分页offset
        :type offset: int
        :param limit: 分页limit
        :type limit: int
        :param filter: 过滤
        :type filter: list of filter
        
        """
        req = self.model_v20180525.CheckInstancesUpgradeAbleRequest()
        req.ClusterId = cluster_id
        req.InstanceIds = instance_ids
        req.UpgradeType = upgrade_type
        req.Offset = offset
        req.Limit = limit
        req.Filter = filter
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.CheckInstancesUpgradeAble(req)
        return response

    @retry_with_conditions(3, 10)
    def create_backup_storage_location(self, storage_region=None, bucket=None, name=None, provider=None, path=None, **kwargs):
        """创建备份仓库，指定了存储仓库类型（如COS）、COS桶地区、名称等信息，当前最多允许创建100个仓库， 注意此接口当前是全局接口，多个地域的TKE集群如果要备份到相同的备份仓库中，不需要重复创建备份仓库
        :param storage_region: 存储仓库所属地域，比如COS广州(ap-guangzhou)
        :type storage_region: str
        :param bucket: 对象存储桶名称，如果是COS必须是tke-backup前缀开头
        :type bucket: str
        :param name: 备份仓库名称
        :type name: str
        :param provider: 存储服务提供方，默认腾讯云
        :type provider: str
        :param path: 对象存储桶路径
        :type path: str
        
        """
        req = self.model_v20180525.CreateBackupStorageLocationRequest()
        req.StorageRegion = storage_region
        req.Bucket = bucket
        req.Name = name
        req.Provider = provider
        req.Path = path
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.CreateBackupStorageLocation(req)
        return response

    @retry_with_conditions(3, 10)
    def create_cls_log_config(self, log_config=None, cluster_id=None, logset_id=None, cluster_type=None, **kwargs):
        """创建日志采集配置
        :param log_config: 日志采集配置的json表达
        :type log_config: str
        :param cluster_id: 集群ID
        :type cluster_id: str
        :param logset_id: CLS日志集ID
        :type logset_id: str
        :param cluster_type: 当前集群类型支持tke、eks
        :type cluster_type: str
        
        """
        req = self.model_v20180525.CreateCLSLogConfigRequest()
        req.LogConfig = log_config
        req.ClusterId = cluster_id
        req.LogsetId = logset_id
        req.ClusterType = cluster_type
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.CreateCLSLogConfig(req)
        return response

    @retry_with_conditions(3, 10)
    def create_cluster(self, cluster_type=None, cluster_cidr_settings=None, run_instances_for_node=None, cluster_basic_settings=None, cluster_advanced_settings=None, instance_advanced_settings=None, existed_instances_for_node=None, instance_data_disk_mount_settings=None, extension_addons=None, cdc_id=None, **kwargs):
        """创建集群
        :param cluster_type: 集群类型，托管集群：MANAGED_CLUSTER，独立集群：INDEPENDENT_CLUSTER。
        :type cluster_type: str
        :param cluster_cidr_settings: 集群容器网络配置信息
        :type cluster_cidr_settings: :class:`tencentcloud.tke.v20180525.models.cluster_cidr_settings`
        :param run_instances_for_node: CVM创建透传参数，json化字符串格式，详见[CVM创建实例](https://cloud.tencent.com/document/product/213/15730)接口。总机型(包括地域)数量不超过10个，相同机型(地域)购买多台机器可以通过设置参数中RunInstances中InstanceCount来实现。
        :type run_instances_for_node: list of run_instances_for_node
        :param cluster_basic_settings: 集群的基本配置信息
        :type cluster_basic_settings: :class:`tencentcloud.tke.v20180525.models.cluster_basic_settings`
        :param cluster_advanced_settings: 集群高级配置信息
        :type cluster_advanced_settings: :class:`tencentcloud.tke.v20180525.models.cluster_advanced_settings`
        :param instance_advanced_settings: 节点高级配置信息
        :type instance_advanced_settings: :class:`tencentcloud.tke.v20180525.models.instance_advanced_settings`
        :param existed_instances_for_node: 已存在实例的配置信息。所有实例必须在同一个VPC中，最大数量不超过100，不支持添加竞价实例。
        :type existed_instances_for_node: list of existed_instances_for_node
        :param instance_data_disk_mount_settings: CVM类型和其对应的数据盘挂载配置信息
        :type instance_data_disk_mount_settings: list of InstanceDataDiskMountSetting
        :param extension_addons: 需要安装的扩展组件信息
        :type extension_addons: list of ExtensionAddon
        :param cdc_id: 本地专用集群Id
        :type cdc_id: str
        
        """
        req = self.model_v20180525.CreateClusterRequest()
        req.ClusterType = cluster_type
        req.ClusterCIDRSettings = cluster_cidr_settings
        req.RunInstancesForNode = run_instances_for_node
        req.ClusterBasicSettings = cluster_basic_settings
        req.ClusterAdvancedSettings = cluster_advanced_settings
        req.InstanceAdvancedSettings = instance_advanced_settings
        req.ExistedInstancesForNode = existed_instances_for_node
        req.InstanceDataDiskMountSettings = instance_data_disk_mount_settings
        req.ExtensionAddons = extension_addons
        req.CdcId = cdc_id
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.CreateCluster(req)
        return response

    @retry_with_conditions(3, 10)
    def create_cluster_endpoint(self, cluster_id=None, subnet_id=None, is_extranet=None, domain=None, security_group=None, extensive_parameters=None, **kwargs):
        """创建集群访问端口
        :param cluster_id: 集群ID
        :type cluster_id: str
        :param subnet_id: 集群端口所在的子网ID  (仅在开启非外网访问时需要填，必须为集群所在VPC内的子网)
        :type subnet_id: str
        :param is_extranet: 是否为外网访问（TRUE 外网访问 FALSE 内网访问，默认值： FALSE）
        :type is_extranet: bool
        :param domain: 设置域名
        :type domain: str
        :param security_group: 使用的安全组，只有外网访问需要传递（开启外网访问且不使用已有clb时必传）
        :type security_group: str
        :param extensive_parameters: 创建lb参数，只有外网访问需要设置，是一个json格式化后的字符串：{"InternetAccessible":{"InternetChargeType":"TRAFFIC_POSTPAID_BY_HOUR","InternetMaxBandwidthOut":200},"VipIsp":"","BandwidthPackageId":""}。
各个参数意义：
InternetAccessible.InternetChargeType含义：TRAFFIC_POSTPAID_BY_HOUR按流量按小时后计费;BANDWIDTH_POSTPAID_BY_HOUR 按带宽按小时后计费;InternetAccessible.BANDWIDTH_PACKAGE 按带宽包计费。
InternetMaxBandwidthOut含义：最大出带宽，单位Mbps，范围支持0到2048，默认值10。
VipIsp含义：CMCC | CTCC | CUCC，分别对应 移动 | 电信 | 联通，如果不指定本参数，则默认使用BGP。可通过 DescribeSingleIsp 接口查询一个地域所支持的Isp。如果指定运营商，则网络计费式只能使用按带宽包计费BANDWIDTH_PACKAGE。
BandwidthPackageId含义：带宽包ID，指定此参数时，网络计费方式InternetAccessible.InternetChargeType只支持按带宽包计费BANDWIDTH_PACKAGE。
        :type extensive_parameters: str
        
        """
        req = self.model_v20180525.CreateClusterEndpointRequest()
        req.ClusterId = cluster_id
        req.SubnetId = subnet_id
        req.IsExtranet = is_extranet
        req.Domain = domain
        req.SecurityGroup = security_group
        req.ExtensiveParameters = extensive_parameters
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.CreateClusterEndpoint(req)
        return response

    @retry_with_conditions(3, 10)
    def create_cluster_endpoint_vip(self, cluster_id=None, security_policies=None, **kwargs):
        """创建托管集群外网访问端口（不再维护，准备下线）请使用新接口：CreateClusterEndpoint
        :param cluster_id: 集群ID
        :type cluster_id: str
        :param security_policies: 安全策略放通单个IP或CIDR(例如: "192.168.1.0/24",默认为拒绝所有)
        :type security_policies: list of str
        
        """
        req = self.model_v20180525.CreateClusterEndpointVipRequest()
        req.ClusterId = cluster_id
        req.SecurityPolicies = security_policies
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.CreateClusterEndpointVip(req)
        return response

    @retry_with_conditions(3, 10)
    def create_cluster_instances(self, cluster_id=None, run_instance_para=None, instance_advanced_settings=None, skip_validate_options=None, **kwargs):
        """扩展(新建)集群节点
        :param cluster_id: 集群 ID，请填写 查询集群列表 接口中返回的 clusterId 字段
        :type cluster_id: str
        :param run_instance_para: CVM创建透传参数，json化字符串格式，如需要保证扩展集群节点请求幂等性需要在此参数添加ClientToken字段，详见[CVM创建实例](https://cloud.tencent.com/document/product/213/15730)接口。
        :type run_instance_para: str
        :param instance_advanced_settings: 实例额外需要设置参数信息
        :type instance_advanced_settings: :class:`tencentcloud.tke.v20180525.models.instance_advanced_settings`
        :param skip_validate_options: 校验规则相关选项，可配置跳过某些校验规则。目前支持GlobalRouteCIDRCheck（跳过GlobalRouter的相关校验），VpcCniCIDRCheck（跳过VpcCni相关校验）
        :type skip_validate_options: list of str
        
        """
        req = self.model_v20180525.CreateClusterInstancesRequest()
        req.ClusterId = cluster_id
        req.RunInstancePara = run_instance_para
        req.InstanceAdvancedSettings = instance_advanced_settings
        req.SkipValidateOptions = skip_validate_options
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.CreateClusterInstances(req)
        return response

    @retry_with_conditions(3, 10)
    def create_cluster_node_pool(self, cluster_id=None, auto_scaling_group_para=None, launch_configure_para=None, instance_advanced_settings=None, enable_autoscale=None, name=None, labels=None, taints=None, annotations=None, container_runtime=None, runtime_version=None, node_pool_os=None, os_customize_type=None, tags=None, deletion_protection=None, **kwargs):
        """创建节点池
        :param cluster_id: cluster id
        :type cluster_id: str
        :param auto_scaling_group_para: auto_scaling_group_para AS组参数，参考 https://cloud.tencent.com/document/product/377/20440
        :type auto_scaling_group_para: str
        :param launch_configure_para: launch_configure_para 运行参数，参考 https://cloud.tencent.com/document/product/377/20447
        :type launch_configure_para: str
        :param instance_advanced_settings: instance_advanced_settings
        :type instance_advanced_settings: :class:`tencentcloud.tke.v20180525.models.instance_advanced_settings`
        :param enable_autoscale: 是否启用自动伸缩
        :type enable_autoscale: bool
        :param name: 节点池名称
        :type name: str
        :param labels: labels标签
        :type labels: list of Label
        :param taints: taints互斥
        :type taints: list of Taint
        :param annotations: 节点Annotation 列表
        :type annotations: list of AnnotationValue
        :param container_runtime: 节点池纬度运行时类型及版本
        :type container_runtime: str
        :param runtime_version: 运行时版本
        :type runtime_version: str
        :param node_pool_os: 节点池os，当为自定义镜像时，传镜像id；否则为公共镜像的osname
        :type node_pool_os: str
        :param os_customize_type: 容器的镜像版本，"DOCKER_CUSTOMIZE"(容器定制版),"GENERAL"(普通版本，默认值)
        :type os_customize_type: str
        :param tags: 资源标签
        :type tags: list of Tag
        :param deletion_protection: 删除保护开关
        :type deletion_protection: bool
        
        """
        req = self.model_v20180525.CreateClusterNodePoolRequest()
        req.ClusterId = cluster_id
        req.AutoScalingGroupPara = auto_scaling_group_para
        req.LaunchConfigurePara = launch_configure_para
        req.InstanceAdvancedSettings = instance_advanced_settings
        req.EnableAutoscale = enable_autoscale
        req.Name = name
        req.Labels = labels
        req.Taints = taints
        req.Annotations = annotations
        req.ContainerRuntime = container_runtime
        req.RuntimeVersion = runtime_version
        req.NodePoolOs = node_pool_os
        req.OsCustomizeType = os_customize_type
        req.Tags = tags
        req.DeletionProtection = deletion_protection
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.CreateClusterNodePool(req)
        return response

    @retry_with_conditions(3, 10)
    def create_cluster_release(self, cluster_id=None, name=None, namespace=None, chart=None, values=None, chart_from=None, chart_version=None, chart_repo_url=None, username=None, password=None, chart_namespace=None, cluster_type=None, **kwargs):
        """集群创建应用
        :param cluster_id: 集群ID
        :type cluster_id: str
        :param name: 应用名称
        :type name: str
        :param namespace: 应用命名空间
        :type namespace: str
        :param chart: 制品名称或从第三方repo 安装chart时，制品压缩包下载地址, 不支持重定向类型chart 地址，结尾为*.tgz
        :type chart: str
        :param values: 自定义参数
        :type values: :class:`tencentcloud.tke.v20180525.models.Releasevalues`
        :param chartFrom: 制品来源，范围：tke-market 或 other默认值：tke-market。
        :type chartFrom: str
        :param chartVersion: 制品版本
        :type chartVersion: str
        :param chartRepoURL: 制品仓库URL地址
        :type chartRepoURL: str
        :param username: 制品访问用户名
        :type username: str
        :param password: 制品访问密码
        :type password: str
        :param chartnamespace: 制品命名空间，chartFrom为tke-market时chartnamespace不为空，值为DescribeProducts接口反馈的namespace
        :type chartnamespace: str
        :param cluster_type: 集群类型，支持传 tke, eks, tkeedge, external(注册集群）
        :type cluster_type: str
        
        """
        req = self.model_v20180525.CreateClusterReleaseRequest()
        req.ClusterId = cluster_id
        req.Name = name
        req.Namespace = namespace
        req.Chart = chart
        req.Values = values
        req.ChartFrom = chart_from
        req.ChartVersion = chart_version
        req.ChartRepoURL = chart_repo_url
        req.Username = username
        req.Password = password
        req.ChartNamespace = chart_namespace
        req.ClusterType = cluster_type
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.CreateClusterRelease(req)
        return response

    @retry_with_conditions(3, 10)
    def create_cluster_route(self, route_table_name=None, destination_cidr_block=None, gateway_ip=None, **kwargs):
        """创建集群路由
        :param route_table_name: 路由表名称。
        :type route_table_name: str
        :param destination_cidr_block: 目的节点的 PodCIDR
        :type destination_cidr_block: str
        :param gateway_ip: 下一跳地址，即目的节点的内网 IP 地址
        :type gateway_ip: str
        
        """
        req = self.model_v20180525.CreateClusterRouteRequest()
        req.RouteTableName = route_table_name
        req.DestinationCidrBlock = destination_cidr_block
        req.GatewayIp = gateway_ip
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.CreateClusterRoute(req)
        return response

    @retry_with_conditions(3, 10)
    def create_cluster_route_table(self, route_table_name=None, route_table_cidr_block=None, vpc_id=None, ignore_cluster_cidr_conflict=None, **kwargs):
        """创建集群路由表
        :param route_table_name: 路由表名称，一般为集群ID
        :type route_table_name: str
        :param route_table_cidr_block: 路由表CIDR
        :type route_table_cidr_block: str
        :param vpc_id: 路由表绑定的VPC
        :type vpc_id: str
        :param ignore_cluster_cidr_conflict: 是否忽略CIDR与 vpc 路由表的冲突， 0 表示不忽略，1表示忽略。默认不忽略
        :type ignore_cluster_cidr_conflict: int
        
        """
        req = self.model_v20180525.CreateClusterRouteTableRequest()
        req.RouteTableName = route_table_name
        req.RouteTableCidrBlock = route_table_cidr_block
        req.VpcId = vpc_id
        req.IgnoreClusterCidrConflict = ignore_cluster_cidr_conflict
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.CreateClusterRouteTable(req)
        return response

    @retry_with_conditions(3, 10)
    def create_cluster_virtual_node(self, cluster_id=None, node_pool_id=None, subnet_id=None, subnet_ids=None, virtual_nodes=None, **kwargs):
        """创建按量计费超级节点
        :param cluster_id: 集群ID
        :type cluster_id: str
        :param node_pool_id: 虚拟节点所属节点池
        :type node_pool_id: str
        :param subnet_id: 虚拟节点所属子网
        :type subnet_id: str
        :param subnet_ids: 虚拟节点子网ID列表，和参数subnet_id互斥
        :type subnet_ids: list of str
        :param virtual_nodes: 虚拟节点列表
        :type virtual_nodes: list of VirtualNodeSpec
        
        """
        req = self.model_v20180525.CreateClusterVirtualNodeRequest()
        req.ClusterId = cluster_id
        req.NodePoolId = node_pool_id
        req.SubnetId = subnet_id
        req.SubnetIds = subnet_ids
        req.VirtualNodes = virtual_nodes
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.CreateClusterVirtualNode(req)
        return response

    @retry_with_conditions(3, 10)
    def create_cluster_virtual_node_pool(self, cluster_id=None, name=None, subnet_ids=None, security_group_ids=None, labels=None, taints=None, virtual_nodes=None, deletion_protection=None, os=None, **kwargs):
        """创建超级节点池
        :param cluster_id: 集群Id
        :type cluster_id: str
        :param name: 节点池名称
        :type name: str
        :param subnet_ids: 子网ID列表
        :type subnet_ids: list of str
        :param security_group_ids: 安全组ID列表
        :type security_group_ids: list of str
        :param labels: 虚拟节点label
        :type labels: list of Label
        :param taints: 虚拟节点taint
        :type taints: list of Taint
        :param virtual_nodes: 节点列表
        :type virtual_nodes: list of VirtualNodeSpec
        :param deletion_protection: 删除保护开关
        :type deletion_protection: bool
        :param os: 节点池操作系统：
- linux（默认）
- windows
        :type os: str
        
        """
        req = self.model_v20180525.CreateClusterVirtualNodePoolRequest()
        req.ClusterId = cluster_id
        req.Name = name
        req.SubnetIds = subnet_ids
        req.SecurityGroupIds = security_group_ids
        req.Labels = labels
        req.Taints = taints
        req.VirtualNodes = virtual_nodes
        req.DeletionProtection = deletion_protection
        req.OS = os
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.CreateClusterVirtualNodePool(req)
        return response

    @retry_with_conditions(3, 10)
    def create_ecm_instances(self, cluster_id=None, module_id=None, zone_instance_count_isp_set=None, password=None, internet_max_bandwidth_out=None, image_id=None, instance_name=None, host_name=None, enhanced_service=None, user_data=None, external=None, security_group_ids=None, **kwargs):
        """创建边缘计算ECM机器
        :param cluster_id: 集群id，边缘集群需要先开启公网访问才能添加ecm节点
        :type cluster_id: str
        :param module_id: 边缘模块id
        :type module_id: str
        :param zone_instance_count_isp_set: 需要创建实例的可用区及创建数目及运营商的列表
        :type zone_instance_count_isp_set: list of ECMZoneInstanceCountISP
        :param password: 密码
        :type password: str
        :param internet_max_bandwidth_out: 公网带宽
        :type internet_max_bandwidth_out: int
        :param image_id: 镜像id
        :type image_id: str
        :param instance_name: 实例名称
        :type instance_name: str
        :param host_name: 主机名称
        :type host_name: str
        :param enhanced_service: 增强服务，包括云镜和云监控
        :type enhanced_service: :class:`tencentcloud.tke.v20180525.models.ECMenhanced_service`
        :param user_data: 用户自定义脚本
        :type user_data: str
        :param external: 实例扩展信息
        :type external: str
        :param security_group_ids: 实例所属安全组
        :type security_group_ids: list of str
        
        """
        req = self.model_v20180525.CreateECMInstancesRequest()
        req.ClusterID = cluster_id
        req.ModuleId = module_id
        req.ZoneInstanceCountISPSet = zone_instance_count_isp_set
        req.Password = password
        req.InternetMaxBandwidthOut = internet_max_bandwidth_out
        req.ImageId = image_id
        req.InstanceName = instance_name
        req.HostName = host_name
        req.EnhancedService = enhanced_service
        req.UserData = user_data
        req.External = external
        req.SecurityGroupIds = security_group_ids
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.CreateECMInstances(req)
        return response

    @retry_with_conditions(3, 10)
    def create_eks_cluster(self, k8_s_version=None, vpc_id=None, cluster_name=None, subnet_ids=None, cluster_desc=None, service_subnet_id=None, dns_servers=None, extra_param=None, enable_vpc_core_dns=None, tag_specification=None, subnet_infos=None, **kwargs):
        """创建弹性集群
        :param k8_s_version: k8s版本号。可为1.18.4 1.20.6。
        :type k8_s_version: str
        :param vpc_id: vpc 的Id
        :type vpc_id: str
        :param cluster_name: 集群名称
        :type cluster_name: str
        :param subnet_ids: 子网Id 列表
        :type subnet_ids: list of str
        :param cluster_desc: 集群描述信息
        :type cluster_desc: str
        :param service_subnet_id: Service CIDR 或 Serivce 所在子网Id
        :type service_subnet_id: str
        :param dns_servers: 集群自定义的Dns服务器信息
        :type dns_servers: list of DnsServerConf
        :param extra_param: 扩展参数。须是map[string]string 的json 格式。
        :type extra_param: str
        :param enable_vpc_core_dns: 是否在用户集群内开启Dns。默认为true
        :type enable_vpc_core_dns: bool
        :param tag_specification: 标签描述列表。通过指定该参数可以同时绑定标签到相应的资源实例，当前仅支持绑定标签到集群实例。
        :type tag_specification: list of tag_specification
        :param subnet_infos: 子网信息列表
        :type subnet_infos: list of subnet_infos
        
        """
        req = self.model_v20180525.CreateEKSClusterRequest()
        req.K8SVersion = k8_s_version
        req.VpcId = vpc_id
        req.ClusterName = cluster_name
        req.SubnetIds = subnet_ids
        req.ClusterDesc = cluster_desc
        req.ServiceSubnetId = service_subnet_id
        req.DnsServers = dns_servers
        req.ExtraParam = extra_param
        req.EnableVpcCoreDNS = enable_vpc_core_dns
        req.TagSpecification = tag_specification
        req.SubnetInfos = subnet_infos
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.CreateEKSCluster(req)
        return response

    @retry_with_conditions(3, 10)
    def create_eks_container_instances(self, containers=None, eks_ci_name=None, security_group_ids=None, subnet_id=None, vpc_id=None, memory=None, cpu=None, restart_policy=None, image_registry_credentials=None, eks_ci_volume=None, replicas=None, init_containers=None, dns_config=None, existed_eip_ids=None, auto_create_eip_attribute=None, auto_create_eip=None, cpu_type=None, gpu_type=None, gpu_count=None, cam_role_name=None, **kwargs):
        """创建容器实例
        :param containers: 容器组
        :type containers: list of Container
        :param eks_ci_name: EKS Container Instance容器实例名称
        :type eks_ci_name: str
        :param security_group_ids: 指定新创建实例所属于的安全组Id
        :type security_group_ids: list of str
        :param subnet_id: 实例所属子网Id
        :type subnet_id: str
        :param vpc_id: 实例所属VPC的Id
        :type vpc_id: str
        :param memory: 内存，单位：GiB。可参考[资源规格](https://cloud.tencent.com/document/product/457/39808)文档
        :type memory: float
        :param cpu: CPU，单位：核。可参考[资源规格](https://cloud.tencent.com/document/product/457/39808)文档
        :type cpu: float
        :param restart_policy: 实例重启策略： Always(总是重启)、Never(从不重启)、OnFailure(失败时重启)，默认：Always。
        :type restart_policy: str
        :param image_registry_credentials: 镜像仓库凭证数组
        :type image_registry_credentials: list of ImageRegistryCredential
        :param eks_ci_volume: 数据卷，包含NfsVolume数组和CbsVolume数组
        :type eks_ci_volume: :class:`tencentcloud.tke.v20180525.models.eks_ci_volume`
        :param replicas: 实例副本数，默认为1
        :type replicas: int
        :param _Initcontainers: Init 容器
        :type Initcontainers: list of Container
        :param dns_config: 自定义DNS配置
        :type dns_config: :class:`tencentcloud.tke.v20180525.models.DNSConfig`
        :param existed_eip_ids: 用来绑定容器实例的已有EIP的列表。如传值，需要保证数值和replicas相等。
另外此参数和auto_create_eip_attribute互斥。
        :type existed_eip_ids: list of str
        :param auto_create_eip_attribute: 自动创建EIP的可选参数。若传此参数，则会自动创建EIP。
另外此参数和existed_eip_ids互斥
        :type auto_create_eip_attribute: :class:`tencentcloud.tke.v20180525.models.EipAttribute`
        :param auto_create_eip: 是否为容器实例自动创建EIP，默认为false。若传true，则此参数和existed_eip_ids互斥
        :type auto_create_eip: bool
        :param cpuType: Pod 所需的 CPU 资源型号，如果不填写则默认不强制指定 CPU 类型。目前支持型号如下：
intel
amd
- 支持优先级顺序写法，如 “amd,intel” 表示优先创建 amd 资源 Pod，如果所选地域可用区 amd 资源不足，则会创建 intel 资源 Pod。
        :type cpuType: str
        :param gpu_type: 容器实例所需的 GPU 资源型号，目前支持型号如下：
1/4\*V100
1/2\*V100
V100
1/4\*T4
1/2\*T4
T4
        :type gpu_type: str
        :param gpu_count: Pod 所需的 GPU 数量，如填写，请确保为支持的规格。默认单位为卡，无需再次注明。
        :type gpu_count: int
        :param cam_role_name: 为容器实例关联 CAM 角色，value 填写 CAM 角色名称，容器实例可获取该 CAM 角色包含的权限策略，方便 容器实例 内的程序进行如购买资源、读写存储等云资源操作。
        :type cam_role_name: str
        
        """
        req = self.model_v20180525.CreateEKSContainerInstancesRequest()
        req.Containers = containers
        req.EksCiName = eks_ci_name
        req.SecurityGroupIds = security_group_ids
        req.SubnetId = subnet_id
        req.VpcId = vpc_id
        req.Memory = memory
        req.Cpu = cpu
        req.RestartPolicy = restart_policy
        req.ImageRegistryCredentials = image_registry_credentials
        req.EksCiVolume = eks_ci_volume
        req.Replicas = replicas
        req.InitContainers = init_containers
        req.DnsConfig = dns_config
        req.ExistedEipIds = existed_eip_ids
        req.AutoCreateEipAttribute = auto_create_eip_attribute
        req.AutoCreateEip = auto_create_eip
        req.CpuType = cpu_type
        req.GpuType = gpu_type
        req.GpuCount = gpu_count
        req.CamRoleName = cam_role_name
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.CreateEKSContainerInstances(req)
        return response

    @retry_with_conditions(3, 10)
    def create_edge_cvm_instances(self, cluster_id=None, run_instance_para=None, cvm_region=None, cvm_count=None, external=None, user_script=None, enable_eni=None, **kwargs):
        """创建边缘容器CVM机器
        :param cluster_id: 集群id，边缘集群需要先开启公网访问才能添加cvm节点
        :type cluster_id: str
        :param run_instance_para: CVM创建透传参数，json化字符串格式，如需要保证扩展集群节点请求幂等性需要在此参数添加ClientToken字段，详见[CVM创建实例](https://cloud.tencent.com/document/product/213/15730)接口。
        :type run_instance_para: str
        :param cvm_region: CVM所属Region
        :type cvm_region: str
        :param cvm_count: CVM数量
        :type cvm_count: int
        :param external: 实例扩展信息
        :type external: str
        :param user_script: 用户自定义脚本
        :type user_script: str
        :param enable_eni: 是否开启弹性网卡功能
        :type enable_eni: bool
        
        """
        req = self.model_v20180525.CreateEdgeCVMInstancesRequest()
        req.ClusterID = cluster_id
        req.RunInstancePara = run_instance_para
        req.CvmRegion = cvm_region
        req.CvmCount = cvm_count
        req.External = external
        req.UserScript = user_script
        req.EnableEni = enable_eni
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.CreateEdgeCVMInstances(req)
        return response

    @retry_with_conditions(3, 10)
    def create_edge_log_config(self, cluster_id=None, log_config=None, logset_id=None, **kwargs):
        """创建边缘集群日志采集配置
        :param cluster_id: 集群ID
        :type cluster_id: str
        :param log_config: 日志采集配置的json表达
        :type log_config: str
        :param logset_id: CLS日志集ID
        :type logset_id: str
        
        """
        req = self.model_v20180525.CreateEdgeLogConfigRequest()
        req.ClusterId = cluster_id
        req.LogConfig = log_config
        req.LogsetId = logset_id
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.CreateEdgeLogConfig(req)
        return response

    @retry_with_conditions(3, 10)
    def create_eks_log_config(self, cluster_id=None, log_config=None, logset_id=None, **kwargs):
        """为弹性集群创建日志采集配置
        :param cluster_id: 集群ID
        :type cluster_id: str
        :param log_config: 日志采集配置的json表达
        :type log_config: str
        :param logset_id: 日志集ID
        :type logset_id: str
        
        """
        req = self.model_v20180525.CreateEksLogConfigRequest()
        req.ClusterId = cluster_id
        req.LogConfig = log_config
        req.LogsetId = logset_id
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.CreateEksLogConfig(req)
        return response

    @retry_with_conditions(3, 10)
    def create_image_cache(self, images=None, subnet_id=None, vpc_id=None, image_cache_name=None, security_group_ids=None, image_registry_credentials=None, existed_eip_id=None, auto_create_eip=None, auto_create_eip_attribute=None, image_cache_size=None, retention_days=None, registry_skip_verify_list=None, registry_http_end_point_list=None, resolve_config=None, **kwargs):
        """创建镜像缓存的接口。创建过程中，请勿删除EKSCI实例和云盘，否则镜像缓存将创建失败。
        :param images: 用于制作镜像缓存的容器镜像列表
        :type images: list of str
        :param subnet_id: 实例所属子网 ID
        :type subnet_id: str
        :param vpc_id: 实例所属 VPC ID
        :type vpc_id: str
        :param image_cache_name: 镜像缓存名称
        :type image_cache_name: str
        :param security_group_ids: 安全组 ID
        :type security_group_ids: list of str
        :param image_registry_credentials: 镜像仓库凭证数组
        :type image_registry_credentials: list of ImageRegistryCredential
        :param existed_eip_id: 用来绑定容器实例的已有EIP
        :type existed_eip_id: str
        :param auto_create_eip: 是否为容器实例自动创建EIP，默认为false。若传true，则此参数和existed_eip_ids互斥
        :type auto_create_eip: bool
        :param auto_create_eipAttribute: 自动创建EIP的可选参数。若传此参数，则会自动创建EIP。
另外此参数和existed_eip_ids互斥
        :type auto_create_eipAttribute: :class:`tencentcloud.tke.v20180525.models.EipAttribute`
        :param image_cache_size: 镜像缓存的大小。默认为20 GiB。取值范围参考[云硬盘类型](https://cloud.tencent.com/document/product/362/2353)中的高性能云盘类型的大小限制。
        :type image_cache_size: int
        :param retention_days: 镜像缓存保留时间天数，过期将会自动清理，默认为0，永不过期。
        :type retention_days: int
        :param registry_skip_verify_list: 指定拉取镜像仓库的镜像时不校验证书。如["harbor.example.com"]。
        :type registry_skip_verify_list: list of str
        :param registry_http_end_point_list: 指定拉取镜像仓库的镜像时使用 HTTP 协议。如["harbor.example.com"]。
        :type registry_http_end_point_list: list of str
        :param resolve_config: 自定义制作镜像缓存过程中容器实例的宿主机上的 DNS。如：
"nameserver 4.4.4.4\nnameserver 8.8.8.8"
        :type resolve_config: str
        
        """
        req = self.model_v20180525.CreateImageCacheRequest()
        req.Images = images
        req.SubnetId = subnet_id
        req.VpcId = vpc_id
        req.ImageCacheName = image_cache_name
        req.SecurityGroupIds = security_group_ids
        req.ImageRegistryCredentials = image_registry_credentials
        req.ExistedEipId = existed_eip_id
        req.AutoCreateEip = auto_create_eip
        req.AutoCreateEipAttribute = auto_create_eip_attribute
        req.ImageCacheSize = image_cache_size
        req.RetentionDays = retention_days
        req.RegistrySkipVerifyList = registry_skip_verify_list
        req.RegistryHttpEndPointList = registry_http_end_point_list
        req.ResolveConfig = resolve_config
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.CreateImageCache(req)
        return response

    @retry_with_conditions(3, 10)
    def create_prometheus_alert_policy(self, instance_id=None, alert_rule=None, **kwargs):
        """创建告警策略
        :param instance_id: 实例id
        :type instance_id: str
        :param alert_rule: 告警配置
        :type alert_rule: :class:`tencentcloud.tke.v20180525.models.PrometheusAlertPolicyItem`
        
        """
        req = self.model_v20180525.CreatePrometheusAlertPolicyRequest()
        req.InstanceId = instance_id
        req.AlertRule = alert_rule
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.CreatePrometheusAlertPolicy(req)
        return response

    @retry_with_conditions(3, 10)
    def create_prometheus_alert_rule(self, instance_id=None, alert_rule=None, **kwargs):
        """创建告警规则
        :param instance_id: 实例id
        :type instance_id: str
        :param alert_rule: 告警配置
        :type alert_rule: :class:`tencentcloud.tke.v20180525.models.Prometheusalert_ruleDetail`
        
        """
        req = self.model_v20180525.CreatePrometheusAlertRuleRequest()
        req.InstanceId = instance_id
        req.AlertRule = alert_rule
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.CreatePrometheusAlertRule(req)
        return response

    @retry_with_conditions(3, 10)
    def create_prometheus_cluster_agent(self, instance_id=None, agents=None, **kwargs):
        """与云监控融合的2.0实例关联集群
        :param instance_id: 实例ID
        :type instance_id: str
        :param agents: agent列表
        :type agents: list of PrometheusClusterAgentBasic
        
        """
        req = self.model_v20180525.CreatePrometheusClusterAgentRequest()
        req.InstanceId = instance_id
        req.Agents = agents
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.CreatePrometheusClusterAgent(req)
        return response

    @retry_with_conditions(3, 10)
    def create_prometheus_config(self, instance_id=None, cluster_type=None, cluster_id=None, service_monitors=None, pod_monitors=None, raw_jobs=None, probes=None, **kwargs):
        """创建集群采集配置
        :param instance_id: 实例id
        :type instance_id: str
        :param cluster_type: 集群类型
        :type cluster_type: str
        :param cluster_id: 集群id
        :type cluster_id: str
        :param service_monitors: service_monitors配置
        :type service_monitors: list of PrometheusConfigItem
        :param pod_monitors: pod_monitors配置
        :type pod_monitors: list of PrometheusConfigItem
        :param raw_jobs: prometheus原生Job配置
        :type raw_jobs: list of PrometheusConfigItem
        :param probes: Probe 配置
        :type probes: list of PrometheusConfigItem
        
        """
        req = self.model_v20180525.CreatePrometheusConfigRequest()
        req.InstanceId = instance_id
        req.ClusterType = cluster_type
        req.ClusterId = cluster_id
        req.ServiceMonitors = service_monitors
        req.PodMonitors = pod_monitors
        req.RawJobs = raw_jobs
        req.Probes = probes
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.CreatePrometheusConfig(req)
        return response

    @retry_with_conditions(3, 10)
    def create_prometheus_dashboard(self, instance_id=None, dashboard_name=None, contents=None, **kwargs):
        """创建grafana监控面板
        :param instance_id: 实例id
        :type instance_id: str
        :param dashboard_name: 面板组名称
        :type dashboard_name: str
        :param contents: 面板列表
每一项是一个grafana dashboard的json定义
        :type contents: list of str
        
        """
        req = self.model_v20180525.CreatePrometheusDashboardRequest()
        req.InstanceId = instance_id
        req.DashboardName = dashboard_name
        req.Contents = contents
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.CreatePrometheusDashboard(req)
        return response

    @retry_with_conditions(3, 10)
    def create_prometheus_global_notification(self, instance_id=None, notification=None, **kwargs):
        """创建全局告警通知渠道
        :param instance_id: 实例ID
        :type instance_id: str
        :param notification: 告警通知渠道
        :type notification: :class:`tencentcloud.tke.v20180525.models.PrometheusnotificationItem`
        
        """
        req = self.model_v20180525.CreatePrometheusGlobalNotificationRequest()
        req.InstanceId = instance_id
        req.Notification = notification
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.CreatePrometheusGlobalNotification(req)
        return response

    @retry_with_conditions(3, 10)
    def create_prometheus_record_rule_yaml(self, instance_id=None, content=None, **kwargs):
        """创建聚合规则yaml方式
        :param instance_id: 实例id
        :type instance_id: str
        :param content: yaml的内容
        :type content: str
        
        """
        req = self.model_v20180525.CreatePrometheusRecordRuleYamlRequest()
        req.InstanceId = instance_id
        req.Content = content
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.CreatePrometheusRecordRuleYaml(req)
        return response

    @retry_with_conditions(3, 10)
    def create_prometheus_temp(self, template=None, **kwargs):
        """创建一个云原生Prometheus模板
        :param template: 模板设置
        :type template: :class:`tencentcloud.tke.v20180525.models.PrometheusTemp`
        
        """
        req = self.model_v20180525.CreatePrometheusTempRequest()
        req.Template = template
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.CreatePrometheusTemp(req)
        return response

    @retry_with_conditions(3, 10)
    def create_prometheus_template(self, template=None, **kwargs):
        """创建一个云原生Prometheus模板实例
        :param template: 模板设置
        :type template: :class:`tencentcloud.tke.v20180525.models.Prometheustemplate`
        
        """
        req = self.model_v20180525.CreatePrometheusTemplateRequest()
        req.Template = template
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.CreatePrometheusTemplate(req)
        return response

    @retry_with_conditions(3, 10)
    def create_reserved_instances(self, reserved_instance_spec=None, instance_count=None, instance_charge_prepaid=None, instance_name=None, client_token=None, **kwargs):
        """预留券实例的购买会预先扣除本次实例购买所需金额，在调用本接口前请确保账户余额充足。
        :param reserved_instance_spec: 预留券实例规格。
        :type reserved_instance_spec: :class:`tencentcloud.tke.v20180525.models.reserved_instance_spec`
        :param instance_count: 购买实例数量，一次最大购买数量为300。
        :type instance_count: int
        :param instance_charge_prepaid: 预付费模式，即包年包月相关参数设置。通过该参数可以指定包年包月实例的购买时长、是否设置自动续费等属性。
        :type instance_charge_prepaid: :class:`tencentcloud.tke.v20180525.models.instance_charge_prepaid`
        :param instance_name: 预留券名称。
        :type instance_name: str
        :param client_token: 用于保证请求幂等性的字符串。该字符串由客户生成，需保证不同请求之间唯一，最大值不超过64个ASCII字符。若不指定该参数，则无法保证请求的幂等性。
        :type client_token: str
        
        """
        req = self.model_v20180525.CreateReservedInstancesRequest()
        req.ReservedInstanceSpec = reserved_instance_spec
        req.InstanceCount = instance_count
        req.InstanceChargePrepaid = instance_charge_prepaid
        req.InstanceName = instance_name
        req.ClientToken = client_token
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.CreateReservedInstances(req)
        return response

    @retry_with_conditions(3, 10)
    def create_tke_edge_cluster(self, k8_s_version=None, vpc_id=None, cluster_name=None, pod_cidr=None, service_cidr=None, cluster_desc=None, cluster_advanced_settings=None, max_node_pod_num=None, public_lb=None, cluster_level=None, auto_upgrade_cluster_level=None, charge_type=None, edge_version=None, registry_prefix=None, tag_specification=None, **kwargs):
        """创建边缘计算集群
        :param k8_s_version: k8s版本号
        :type k8_s_version: str
        :param vpc_id: vpc 的Id
        :type vpc_id: str
        :param cluster_name: 集群名称
        :type cluster_name: str
        :param pod_cidr: 集群pod cidr
        :type pod_cidr: str
        :param service_cidr: 集群service cidr
        :type service_cidr: str
        :param cluster_desc: 集群描述信息
        :type cluster_desc: str
        :param cluster_advanced_settings: 集群高级设置
        :type cluster_advanced_settings: :class:`tencentcloud.tke.v20180525.models.Edgecluster_advanced_settings`
        :param max_node_pod_num: 节点上最大Pod数量
        :type max_node_pod_num: int
        :param public_lb: 边缘计算集群公网访问LB信息
        :type public_lb: :class:`tencentcloud.tke.v20180525.models.EdgeClusterpublic_lb`
        :param cluster_level: 集群的级别
        :type cluster_level: str
        :param _AutoUpgradecluster_level: 集群是否支持自动升配
        :type AutoUpgradecluster_level: bool
        :param charge_type: 集群计费方式
        :type charge_type: str
        :param edge_version: 边缘集群版本，此版本区别于k8s版本，是整个集群各组件版本集合
        :type edge_version: str
        :param registry_prefix: 边缘组件镜像仓库前缀
        :type registry_prefix: str
        :param tag_specification: 集群绑定的云标签
        :type tag_specification: :class:`tencentcloud.tke.v20180525.models.tag_specification`
        
        """
        req = self.model_v20180525.CreateTKEEdgeClusterRequest()
        req.K8SVersion = k8_s_version
        req.VpcId = vpc_id
        req.ClusterName = cluster_name
        req.PodCIDR = pod_cidr
        req.ServiceCIDR = service_cidr
        req.ClusterDesc = cluster_desc
        req.ClusterAdvancedSettings = cluster_advanced_settings
        req.MaxNodePodNum = max_node_pod_num
        req.PublicLB = public_lb
        req.ClusterLevel = cluster_level
        req.AutoUpgradeClusterLevel = auto_upgrade_cluster_level
        req.ChargeType = charge_type
        req.EdgeVersion = edge_version
        req.RegistryPrefix = registry_prefix
        req.TagSpecification = tag_specification
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.CreateTKEEdgeCluster(req)
        return response

    @retry_with_conditions(3, 10)
    def delete_addon(self, cluster_id=None, addon_name=None, **kwargs):
        """删除一个addon
        :param cluster_id: 集群ID
        :type cluster_id: str
        :param addon_name: addon名称
        :type addon_name: str
        
        """
        req = self.model_v20180525.DeleteAddonRequest()
        req.ClusterId = cluster_id
        req.AddonName = addon_name
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.DeleteAddon(req)
        return response

    @retry_with_conditions(3, 10)
    def delete_backup_storage_location(self, name=None, **kwargs):
        """删除备份仓库
        :param name: 备份仓库名称
        :type name: str
        
        """
        req = self.model_v20180525.DeleteBackupStorageLocationRequest()
        req.Name = name
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.DeleteBackupStorageLocation(req)
        return response

    @retry_with_conditions(3, 10)
    def delete_cluster(self, cluster_id=None, instance_delete_mode=None, resource_delete_options=None, **kwargs):
        """删除集群(YUNAPI V3版本)
        :param cluster_id: 集群ID
        :type cluster_id: str
        :param instance_delete_mode: 集群实例删除时的策略：terminate（销毁实例，仅支持按量计费云主机实例） retain （仅移除，保留实例）
        :type instance_delete_mode: str
        :param resource_delete_options: 集群删除时资源的删除策略，目前支持CBS（默认保留CBS）
        :type resource_delete_options: list of ResourceDeleteOption
        
        """
        req = self.model_v20180525.DeleteClusterRequest()
        req.ClusterId = cluster_id
        req.InstanceDeleteMode = instance_delete_mode
        req.ResourceDeleteOptions = resource_delete_options
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.DeleteCluster(req)
        return response

    @retry_with_conditions(3, 10)
    def delete_cluster_as_groups(self, cluster_id=None, auto_scaling_group_ids=None, keep_instance=None, **kwargs):
        """删除集群伸缩组
        :param cluster_id: 集群ID，通过[DescribeClusters](https://cloud.tencent.com/document/api/457/31862)接口获取。
        :type cluster_id: str
        :param auto_scaling_group_ids: 集群伸缩组ID的列表
        :type auto_scaling_group_ids: list of str
        :param keep_instance: 是否保留伸缩组中的节点(默认值： false(不保留))
        :type keep_instance: bool
        
        """
        req = self.model_v20180525.DeleteClusterAsGroupsRequest()
        req.ClusterId = cluster_id
        req.AutoScalingGroupIds = auto_scaling_group_ids
        req.KeepInstance = keep_instance
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.DeleteClusterAsGroups(req)
        return response

    @retry_with_conditions(3, 10)
    def delete_cluster_endpoint(self, cluster_id=None, is_extranet=None, **kwargs):
        """删除集群访问端口
        :param cluster_id: 集群ID
        :type cluster_id: str
        :param is_extranet: 是否为外网访问（TRUE 外网访问 FALSE 内网访问，默认值： FALSE）
        :type is_extranet: bool
        
        """
        req = self.model_v20180525.DeleteClusterEndpointRequest()
        req.ClusterId = cluster_id
        req.IsExtranet = is_extranet
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.DeleteClusterEndpoint(req)
        return response

    @retry_with_conditions(3, 10)
    def delete_cluster_endpoint_vip(self, cluster_id=None, **kwargs):
        """删除托管集群外网访问端口（老的方式，仅支持托管集群外网端口）
        :param cluster_id: 集群ID
        :type cluster_id: str
        
        """
        req = self.model_v20180525.DeleteClusterEndpointVipRequest()
        req.ClusterId = cluster_id
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.DeleteClusterEndpointVip(req)
        return response

    @retry_with_conditions(3, 10)
    def delete_cluster_instances(self, cluster_id=None, instance_ids=None, instance_delete_mode=None, force_delete=None, **kwargs):
        """删除集群中的实例
        :param cluster_id: 集群ID
        :type cluster_id: str
        :param instance_ids: 主机InstanceId列表
        :type instance_ids: list of str
        :param instance_delete_mode: 集群实例删除时的策略：terminate（销毁实例，仅支持按量计费云主机实例） retain （仅移除，保留实例）
        :type instance_delete_mode: str
        :param force_delete: 是否强制删除(当节点在初始化时，可以指定参数为TRUE)
        :type force_delete: bool
        
        """
        req = self.model_v20180525.DeleteClusterInstancesRequest()
        req.ClusterId = cluster_id
        req.InstanceIds = instance_ids
        req.InstanceDeleteMode = instance_delete_mode
        req.ForceDelete = force_delete
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.DeleteClusterInstances(req)
        return response

    @retry_with_conditions(3, 10)
    def delete_cluster_node_pool(self, cluster_id=None, node_pool_ids=None, keep_instance=None, **kwargs):
        """删除节点池
        :param cluster_id: 节点池对应的 cluster_id
        :type cluster_id: str
        :param node_pool_ids: 需要删除的节点池 Id 列表
        :type node_pool_ids: list of str
        :param keep_instance: 删除节点池时是否保留节点池内节点(节点仍然会被移出集群，但对应的实例不会被销毁)
        :type keep_instance: bool
        
        """
        req = self.model_v20180525.DeleteClusterNodePoolRequest()
        req.ClusterId = cluster_id
        req.NodePoolIds = node_pool_ids
        req.KeepInstance = keep_instance
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.DeleteClusterNodePool(req)
        return response

    @retry_with_conditions(3, 10)
    def delete_cluster_route(self, route_table_name=None, gateway_ip=None, destination_cidr_block=None, **kwargs):
        """删除集群路由
        :param route_table_name: 路由表名称。
        :type route_table_name: str
        :param gateway_ip: 下一跳地址。
        :type gateway_ip: str
        :param destination_cidr_block: 目的端CIDR。
        :type destination_cidr_block: str
        
        """
        req = self.model_v20180525.DeleteClusterRouteRequest()
        req.RouteTableName = route_table_name
        req.GatewayIp = gateway_ip
        req.DestinationCidrBlock = destination_cidr_block
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.DeleteClusterRoute(req)
        return response

    @retry_with_conditions(3, 10)
    def delete_cluster_route_table(self, route_table_name=None, **kwargs):
        """删除集群路由表
        :param route_table_name: 路由表名称
        :type route_table_name: str
        
        """
        req = self.model_v20180525.DeleteClusterRouteTableRequest()
        req.RouteTableName = route_table_name
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.DeleteClusterRouteTable(req)
        return response

    @retry_with_conditions(3, 10)
    def delete_cluster_virtual_node(self, cluster_id=None, node_names=None, force=None, **kwargs):
        """删除超级节点
        :param cluster_id: 集群ID
        :type cluster_id: str
        :param node_names: 虚拟节点列表
        :type node_names: list of str
        :param force: 是否强制删除：如果虚拟节点上有运行中Pod，则非强制删除状态下不会进行删除
        :type force: bool
        
        """
        req = self.model_v20180525.DeleteClusterVirtualNodeRequest()
        req.ClusterId = cluster_id
        req.NodeNames = node_names
        req.Force = force
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.DeleteClusterVirtualNode(req)
        return response

    @retry_with_conditions(3, 10)
    def delete_cluster_virtual_node_pool(self, cluster_id=None, node_pool_ids=None, force=None, **kwargs):
        """删除超级节点池
        :param cluster_id: 集群ID
        :type cluster_id: str
        :param node_pool_ids: 超级节点池ID列表
        :type node_pool_ids: list of str
        :param force: 是否强制删除，在超级节点上有pod的情况下，如果选择非强制删除，则删除会失败
        :type force: bool
        
        """
        req = self.model_v20180525.DeleteClusterVirtualNodePoolRequest()
        req.ClusterId = cluster_id
        req.NodePoolIds = node_pool_ids
        req.Force = force
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.DeleteClusterVirtualNodePool(req)
        return response

    @retry_with_conditions(3, 10)
    def delete_ecm_instances(self, cluster_id=None, ecm_id_set=None, **kwargs):
        """删除ECM实例
        :param cluster_id: 集群ID
        :type cluster_id: str
        :param ecm_id_set: ecm id集合
        :type ecm_id_set: list of str
        
        """
        req = self.model_v20180525.DeleteECMInstancesRequest()
        req.ClusterID = cluster_id
        req.EcmIdSet = ecm_id_set
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.DeleteECMInstances(req)
        return response

    @retry_with_conditions(3, 10)
    def delete_eks_cluster(self, cluster_id=None, **kwargs):
        """删除弹性集群(yunapiv3)
        :param cluster_id: 弹性集群Id
        :type cluster_id: str
        
        """
        req = self.model_v20180525.DeleteEKSClusterRequest()
        req.ClusterId = cluster_id
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.DeleteEKSCluster(req)
        return response

    @retry_with_conditions(3, 10)
    def delete_eks_container_instances(self, eks_ci_ids=None, release_auto_created_eip=None, **kwargs):
        """删除容器实例，可批量删除
        :param eks_ci_ids: 需要删除的EksCi的Id。 最大数量不超过20
        :type eks_ci_ids: list of str
        :param release_auto_created_eip: 是否释放为EksCi自动创建的Eip
        :type release_auto_created_eip: bool
        
        """
        req = self.model_v20180525.DeleteEKSContainerInstancesRequest()
        req.EksCiIds = eks_ci_ids
        req.ReleaseAutoCreatedEip = release_auto_created_eip
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.DeleteEKSContainerInstances(req)
        return response

    @retry_with_conditions(3, 10)
    def delete_edge_cvm_instances(self, cluster_id=None, cvm_id_set=None, **kwargs):
        """删除边缘容器CVM实例
        :param cluster_id: 集群ID
        :type cluster_id: str
        :param cvm_id_set: cvm id集合
        :type cvm_id_set: list of str
        
        """
        req = self.model_v20180525.DeleteEdgeCVMInstancesRequest()
        req.ClusterID = cluster_id
        req.CvmIdSet = cvm_id_set
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.DeleteEdgeCVMInstances(req)
        return response

    @retry_with_conditions(3, 10)
    def delete_edge_cluster_instances(self, cluster_id=None, instance_ids=None, **kwargs):
        """删除边缘计算实例
        :param cluster_id: 集群ID
        :type cluster_id: str
        :param instance_ids: 待删除实例ID数组
        :type instance_ids: list of str
        
        """
        req = self.model_v20180525.DeleteEdgeClusterInstancesRequest()
        req.ClusterId = cluster_id
        req.InstanceIds = instance_ids
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.DeleteEdgeClusterInstances(req)
        return response

    @retry_with_conditions(3, 10)
    def delete_image_caches(self, image_cache_ids=None, **kwargs):
        """批量删除镜像缓存
        :param image_cache_ids: 镜像缓存ID数组
        :type image_cache_ids: list of str
        
        """
        req = self.model_v20180525.DeleteImageCachesRequest()
        req.ImageCacheIds = image_cache_ids
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.DeleteImageCaches(req)
        return response

    @retry_with_conditions(3, 10)
    def delete_log_configs(self, cluster_id=None, log_config_names=None, cluster_type=None, **kwargs):
        """删除集群内采集规则
        :param cluster_id: 集群ID
        :type cluster_id: str
        :param log_config_names: 待删除采集规则名称，多个采集规则使用","分隔
        :type log_config_names: str
        :param cluster_type: 集群集群类型, tke/eks 默认为 tke 集群
        :type cluster_type: str
        
        """
        req = self.model_v20180525.DeleteLogConfigsRequest()
        req.ClusterId = cluster_id
        req.LogConfigNames = log_config_names
        req.ClusterType = cluster_type
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.DeleteLogConfigs(req)
        return response

    @retry_with_conditions(3, 10)
    def delete_prometheus_alert_policy(self, instance_id=None, alert_ids=None, names=None, **kwargs):
        """删除2.0实例告警策略
        :param instance_id: 实例id
        :type instance_id: str
        :param alert_ids: 告警策略id列表
        :type alert_ids: list of str
        :param names: 告警策略名称
        :type names: list of str
        
        """
        req = self.model_v20180525.DeletePrometheusAlertPolicyRequest()
        req.InstanceId = instance_id
        req.AlertIds = alert_ids
        req.Names = names
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.DeletePrometheusAlertPolicy(req)
        return response

    @retry_with_conditions(3, 10)
    def delete_prometheus_alert_rule(self, instance_id=None, alert_ids=None, **kwargs):
        """删除告警规则
        :param instance_id: 实例id
        :type instance_id: str
        :param alert_ids: 告警规则id列表
        :type alert_ids: list of str
        
        """
        req = self.model_v20180525.DeletePrometheusAlertRuleRequest()
        req.InstanceId = instance_id
        req.AlertIds = alert_ids
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.DeletePrometheusAlertRule(req)
        return response

    @retry_with_conditions(3, 10)
    def delete_prometheus_cluster_agent(self, agents=None, instance_id=None, force=None, **kwargs):
        """解除TMP实例的集群关联
        :param agents: agent列表
        :type agents: list of PrometheusAgentInfo
        :param instance_id: 实例id
        :type instance_id: str
        :param force: 在7天可回收期间，强制解除绑定
        :type force: bool
        
        """
        req = self.model_v20180525.DeletePrometheusClusterAgentRequest()
        req.Agents = agents
        req.InstanceId = instance_id
        req.Force = force
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.DeletePrometheusClusterAgent(req)
        return response

    @retry_with_conditions(3, 10)
    def delete_prometheus_config(self, instance_id=None, cluster_type=None, cluster_id=None, service_monitors=None, pod_monitors=None, raw_jobs=None, probes=None, **kwargs):
        """删除集群采集配置
        :param instance_id: 实例id
        :type instance_id: str
        :param cluster_type: 集群类型
        :type cluster_type: str
        :param cluster_id: 集群id
        :type cluster_id: str
        :param service_monitors: 要删除的ServiceMonitor名字列表
        :type service_monitors: list of str
        :param pod_monitors: 要删除的PodMonitor名字列表
        :type pod_monitors: list of str
        :param raw_jobs: 要删除的raw_jobs名字列表
        :type raw_jobs: list of str
        :param probes: 要删除的Probe名字列表
        :type probes: list of str
        
        """
        req = self.model_v20180525.DeletePrometheusConfigRequest()
        req.InstanceId = instance_id
        req.ClusterType = cluster_type
        req.ClusterId = cluster_id
        req.ServiceMonitors = service_monitors
        req.PodMonitors = pod_monitors
        req.RawJobs = raw_jobs
        req.Probes = probes
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.DeletePrometheusConfig(req)
        return response

    @retry_with_conditions(3, 10)
    def delete_prometheus_record_rule_yaml(self, instance_id=None, names=None, **kwargs):
        """删除聚合规则
        :param instance_id: 实例id
        :type instance_id: str
        :param names: 聚合规则列表
        :type names: list of str
        
        """
        req = self.model_v20180525.DeletePrometheusRecordRuleYamlRequest()
        req.InstanceId = instance_id
        req.Names = names
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.DeletePrometheusRecordRuleYaml(req)
        return response

    @retry_with_conditions(3, 10)
    def delete_prometheus_temp(self, template_id=None, **kwargs):
        """删除一个云原生Prometheus配置模板
        :param template_id: 模板id
        :type template_id: str
        
        """
        req = self.model_v20180525.DeletePrometheusTempRequest()
        req.TemplateId = template_id
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.DeletePrometheusTemp(req)
        return response

    @retry_with_conditions(3, 10)
    def delete_prometheus_temp_sync(self, template_id=None, targets=None, **kwargs):
        """解除模板同步，这将会删除目标中该模板所生产的配置，针对V2版本实例
        :param template_id: 模板id
        :type template_id: str
        :param targets: 取消同步的对象列表
        :type targets: list of PrometheusTemplateSyncTarget
        
        """
        req = self.model_v20180525.DeletePrometheusTempSyncRequest()
        req.TemplateId = template_id
        req.Targets = targets
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.DeletePrometheusTempSync(req)
        return response

    @retry_with_conditions(3, 10)
    def delete_prometheus_template(self, template_id=None, **kwargs):
        """删除一个云原生Prometheus配置模板
        :param template_id: 模板id
        :type template_id: str
        
        """
        req = self.model_v20180525.DeletePrometheusTemplateRequest()
        req.TemplateId = template_id
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.DeletePrometheusTemplate(req)
        return response

    @retry_with_conditions(3, 10)
    def delete_prometheus_template_sync(self, template_id=None, targets=None, **kwargs):
        """取消模板同步，这将会删除目标中该模板所生产的配置
        :param template_id: 模板id
        :type template_id: str
        :param targets: 取消同步的对象列表
        :type targets: list of PrometheusTemplateSyncTarget
        
        """
        req = self.model_v20180525.DeletePrometheusTemplateSyncRequest()
        req.TemplateId = template_id
        req.Targets = targets
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.DeletePrometheusTemplateSync(req)
        return response

    @retry_with_conditions(3, 10)
    def delete_reserved_instances(self, reserved_instance_ids=None, **kwargs):
        """预留券实例如符合退还规则，可通过本接口主动退还。
        :param reserved_instance_ids: 预留券实例ID。
        :type reserved_instance_ids: list of str
        
        """
        req = self.model_v20180525.DeleteReservedInstancesRequest()
        req.ReservedInstanceIds = reserved_instance_ids
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.DeleteReservedInstances(req)
        return response

    @retry_with_conditions(3, 10)
    def delete_tke_edge_cluster(self, cluster_id=None, **kwargs):
        """删除边缘计算集群
        :param cluster_id: 集群ID
        :type cluster_id: str
        
        """
        req = self.model_v20180525.DeleteTKEEdgeClusterRequest()
        req.ClusterId = cluster_id
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.DeleteTKEEdgeCluster(req)
        return response

    @retry_with_conditions(3, 10)
    def describe_addon(self, cluster_id=None, addon_name=None, **kwargs):
        """获取addon列表
        :param cluster_id: 集群ID
        :type cluster_id: str
        :param addon_name: addon名称（不传时会返回集群下全部的addon）
        :type addon_name: str
        
        """
        req = self.model_v20180525.DescribeAddonRequest()
        req.ClusterId = cluster_id
        req.AddonName = addon_name
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.DescribeAddon(req)
        return response

    @retry_with_conditions(3, 10)
    def describe_addon_values(self, cluster_id=None, addon_name=None, **kwargs):
        """获取一个addon的参数
        :param cluster_id: 集群ID
        :type cluster_id: str
        :param addon_name: addon名称
        :type addon_name: str
        
        """
        req = self.model_v20180525.DescribeAddonValuesRequest()
        req.ClusterId = cluster_id
        req.AddonName = addon_name
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.DescribeAddonValues(req)
        return response

    @retry_with_conditions(3, 10)
    def describe_available_cluster_version(self, cluster_id=None, cluster_ids=None, **kwargs):
        """获取集群可以升级的所有版本
        :param cluster_id: 集群 Id。若只查询某个集群可升级的版本，需填写此项。
        :type cluster_id: str
        :param cluster_ids: 集群 Id 列表。若查询多个集群可升级的版本，需填写此项。
        :type cluster_ids: list of str
        
        """
        req = self.model_v20180525.DescribeAvailableClusterVersionRequest()
        req.ClusterId = cluster_id
        req.ClusterIds = cluster_ids
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.DescribeAvailableClusterVersion(req)
        return response

    @retry_with_conditions(3, 10)
    def describe_available_tke_edge_version(self, cluster_id=None, **kwargs):
        """边缘计算支持版本和k8s版本
        :param cluster_id: 填写cluster_id获取当前集群各个组件版本和最新版本
        :type cluster_id: str
        
        """
        req = self.model_v20180525.DescribeAvailableTKEEdgeVersionRequest()
        req.ClusterId = cluster_id
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.DescribeAvailableTKEEdgeVersion(req)
        return response

    @retry_with_conditions(3, 10)
    def describe_backup_storage_locations(self, names=None, **kwargs):
        """查询备份仓库信息
        :param names: 多个备份仓库名称，如果不填写，默认返回当前地域所有存储仓库名称
        :type names: list of str
        
        """
        req = self.model_v20180525.DescribeBackupStorageLocationsRequest()
        req.Names = names
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.DescribeBackupStorageLocations(req)
        return response

    @retry_with_conditions(3, 10)
    def describe_batch_modify_tags_status(self, cluster_id=None, **kwargs):
        """查询批量修改标签状态
        :param cluster_id: 集群id
        :type cluster_id: str
        
        """
        req = self.model_v20180525.DescribeBatchModifyTagsStatusRequest()
        req.ClusterId = cluster_id
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.DescribeBatchModifyTagsStatus(req)
        return response

    @retry_with_conditions(3, 10)
    def describe_cluster_as_group_option(self, cluster_id=None, **kwargs):
        """集群弹性伸缩配置
        :param cluster_id: 集群ID
        :type cluster_id: str
        
        """
        req = self.model_v20180525.DescribeClusterAsGroupOptionRequest()
        req.ClusterId = cluster_id
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.DescribeClusterAsGroupOption(req)
        return response

    @retry_with_conditions(3, 10)
    def describe_cluster_as_groups(self, cluster_id=None, auto_scaling_group_ids=None, offset=None, limit=None, **kwargs):
        """集群关联的伸缩组列表
        :param cluster_id: 集群ID
        :type cluster_id: str
        :param auto_scaling_group_ids: 伸缩组ID列表，如果为空，表示拉取集群关联的所有伸缩组。
        :type auto_scaling_group_ids: list of str
        :param offset: 偏移量，默认为0。关于offset的更进一步介绍请参考 API [简介](https://cloud.tencent.com/document/api/213/15688)中的相关小节。
        :type offset: int
        :param limit: 返回数量，默认为20，最大值为100。关于limit的更进一步介绍请参考 API [简介](https://cloud.tencent.com/document/api/213/15688)中的相关小节。
        :type limit: int
        
        """
        req = self.model_v20180525.DescribeClusterAsGroupsRequest()
        req.ClusterId = cluster_id
        req.AutoScalingGroupIds = auto_scaling_group_ids
        req.Offset = offset
        req.Limit = limit
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.DescribeClusterAsGroups(req)
        return response

    @retry_with_conditions(3, 10)
    def describe_cluster_authentication_options(self, cluster_id=None, **kwargs):
        """查看集群认证配置
        :param cluster_id: 集群ID
        :type cluster_id: str
        
        """
        req = self.model_v20180525.DescribeClusterAuthenticationOptionsRequest()
        req.ClusterId = cluster_id
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.DescribeClusterAuthenticationOptions(req)
        return response

    @retry_with_conditions(3, 10)
    def describe_cluster_common_names(self, cluster_id=None, subaccount_uins=None, role_ids=None, **kwargs):
        """获取指定子账户在RBAC授权模式中对应kube-apiserver客户端证书的CommonName字段，如果没有客户端证书，将会签发一个，此接口有最大传入子账户数量上限，当前为50
        :param cluster_id: 集群ID
        :type cluster_id: str
        :param subaccount_uins: 子账户列表，不可超出最大值50
        :type subaccount_uins: list of str
        :param role_ids: 角色ID列表，不可超出最大值50
        :type role_ids: list of str
        
        """
        req = self.model_v20180525.DescribeClusterCommonNamesRequest()
        req.ClusterId = cluster_id
        req.SubaccountUins = subaccount_uins
        req.RoleIds = role_ids
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.DescribeClusterCommonNames(req)
        return response

    @retry_with_conditions(3, 10)
    def describe_cluster_controllers(self, cluster_id=None, **kwargs):
        """用于查询Kubernetes的各个原生控制器是否开启
        :param cluster_id: 集群ID
        :type cluster_id: str
        
        """
        req = self.model_v20180525.DescribeClusterControllersRequest()
        req.ClusterId = cluster_id
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.DescribeClusterControllers(req)
        return response

    @retry_with_conditions(3, 10)
    def describe_cluster_endpoint_status(self, cluster_id=None, is_extranet=None, **kwargs):
        """查询集群访问端口状态(独立集群开启内网/外网访问，托管集群支持开启内网访问)
        :param cluster_id: 集群ID
        :type cluster_id: str
        :param is_extranet: 是否为外网访问（TRUE 外网访问 FALSE 内网访问，默认值： FALSE）
        :type is_extranet: bool
        
        """
        req = self.model_v20180525.DescribeClusterEndpointStatusRequest()
        req.ClusterId = cluster_id
        req.IsExtranet = is_extranet
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.DescribeClusterEndpointStatus(req)
        return response

    @retry_with_conditions(3, 10)
    def describe_cluster_endpoint_vip_status(self, cluster_id=None, **kwargs):
        """查询集群开启端口流程状态(仅支持托管集群外网端口)
        :param cluster_id: 集群ID
        :type cluster_id: str
        
        """
        req = self.model_v20180525.DescribeClusterEndpointVipStatusRequest()
        req.ClusterId = cluster_id
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.DescribeClusterEndpointVipStatus(req)
        return response

    @retry_with_conditions(3, 10)
    def describe_cluster_endpoints(self, cluster_id=None, **kwargs):
        """获取集群的访问地址，包括内网地址，外网地址，外网域名，外网访问安全策略
        :param cluster_id: 集群ID
        :type cluster_id: str
        
        """
        req = self.model_v20180525.DescribeClusterEndpointsRequest()
        req.ClusterId = cluster_id
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.DescribeClusterEndpoints(req)
        return response

    @retry_with_conditions(3, 10)
    def describe_cluster_extra_args(self, cluster_id=None, **kwargs):
        """查询集群自定义参数
        :param cluster_id: 集群ID
        :type cluster_id: str
        
        """
        req = self.model_v20180525.DescribeClusterExtraArgsRequest()
        req.ClusterId = cluster_id
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.DescribeClusterExtraArgs(req)
        return response

    @retry_with_conditions(3, 10)
    def describe_cluster_inspection_results_overview(self, cluster_ids=None, group_by=None, **kwargs):
        """查询用户单个Region下的所有集群巡检结果概览信息
        :param cluster_ids: Array of String	目标集群列表，为空查询用户所有集群

        :type cluster_ids: list of str
        :param group_by: 聚合字段信息，概览结果按照 group_by 信息聚合后返回，可选参数：
catalogue.first：按一级分类聚合
catalogue.second：按二级分类聚合
        :type group_by: list of str
        
        """
        req = self.model_v20180525.DescribeClusterInspectionResultsOverviewRequest()
        req.ClusterIds = cluster_ids
        req.GroupBy = group_by
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.DescribeClusterInspectionResultsOverview(req)
        return response

    @retry_with_conditions(3, 10)
    def describe_cluster_instances(self, cluster_id=None, offset=None, limit=None, instance_ids=None, instance_role=None, filters=None, **kwargs):
        """查询集群下节点实例信息
        :param cluster_id: 集群ID
        :type cluster_id: str
        :param offset: 偏移量，默认为0。关于offset的更进一步介绍请参考 API [简介](https://cloud.tencent.com/document/api/213/15688)中的相关小节。
        :type offset: int
        :param limit: 返回数量，默认为20，最大值为100。关于limit的更进一步介绍请参考 API [简介](https://cloud.tencent.com/document/api/213/15688)中的相关小节。
        :type limit: int
        :param instance_ids: 需要获取的节点实例Id列表。如果为空，表示拉取集群下所有节点实例。
        :type instance_ids: list of str
        :param instance_role: 节点角色, MASTER, WORKER, ETCD, MASTER_ETCD,ALL, 默认为WORKER。默认为WORKER类型。
        :type instance_role: str
        :param filters: 过滤条件列表；Name的可选值为nodepool-id、nodepool-instance-type；Name为nodepool-id表示根据节点池id过滤机器，Value的值为具体的节点池id，Name为nodepool-instance-type表示节点加入节点池的方式，Value的值为MANUALLY_ADDED（手动加入节点池）、AUTOSCALING_ADDED（伸缩组扩容方式加入节点池）、ALL（手动加入节点池 和 伸缩组扩容方式加入节点池）
        :type filters: list of Filter
        
        """
        req = self.model_v20180525.DescribeClusterInstancesRequest()
        req.ClusterId = cluster_id
        req.Offset = offset
        req.Limit = limit
        req.InstanceIds = instance_ids
        req.InstanceRole = instance_role
        req.Filters = filters
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.DescribeClusterInstances(req)
        return response

    @retry_with_conditions(3, 10)
    def describe_cluster_kubeconfig(self, cluster_id=None, is_extranet=None, **kwargs):
        """获取集群的kubeconfig文件，不同子账户获取自己的kubeconfig文件，该文件中有每个子账户自己的kube-apiserver的客户端证书，默认首次调此接口时候创建客户端证书，时效20年，未授予任何权限，如果是集群所有者或者主账户，则默认是cluster-admin权限。
        :param cluster_id: 集群ID
        :type cluster_id: str
        :param is_extranet: 默认false 获取内网，是否获取外网访问的kubeconfig
        :type is_extranet: bool
        
        """
        req = self.model_v20180525.DescribeClusterKubeconfigRequest()
        req.ClusterId = cluster_id
        req.IsExtranet = is_extranet
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.DescribeClusterKubeconfig(req)
        return response

    @retry_with_conditions(3, 10)
    def describe_cluster_level_attribute(self, cluster_id=None, **kwargs):
        """获取集群规模
        :param cluster_id: 集群ID，变配时使用
        :type cluster_id: str
        
        """
        req = self.model_v20180525.DescribeClusterLevelAttributeRequest()
        req.ClusterID = cluster_id
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.DescribeClusterLevelAttribute(req)
        return response

    @retry_with_conditions(3, 10)
    def describe_cluster_level_change_records(self, cluster_id=None, start_at=None, end_at=None, offset=None, limit=None, **kwargs):
        """查询集群变配记录
        :param cluster_id: 集群ID
        :type cluster_id: str
        :param start_at: 开始时间
        :type start_at: str
        :param end_at: 结束时间
        :type end_at: str
        :param offset: 偏移量,默认0
        :type offset: int
        :param limit: 最大输出条数，默认20
        :type limit: int
        
        """
        req = self.model_v20180525.DescribeClusterLevelChangeRecordsRequest()
        req.ClusterID = cluster_id
        req.StartAt = start_at
        req.EndAt = end_at
        req.Offset = offset
        req.Limit = limit
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.DescribeClusterLevelChangeRecords(req)
        return response

    @retry_with_conditions(3, 10)
    def describe_cluster_node_pool_detail(self, cluster_id=None, node_pool_id=None, **kwargs):
        """查询节点池详情
        :param cluster_id: 集群id
        :type cluster_id: str
        :param node_pool_id: 节点池id
        :type node_pool_id: str
        
        """
        req = self.model_v20180525.DescribeClusterNodePoolDetailRequest()
        req.ClusterId = cluster_id
        req.NodePoolId = node_pool_id
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.DescribeClusterNodePoolDetail(req)
        return response

    @retry_with_conditions(3, 10)
    def describe_cluster_node_pools(self, cluster_id=None, filters=None, **kwargs):
        """查询节点池列表
        :param cluster_id: cluster_id（集群id）
        :type cluster_id: str
        :param filters: · "Name":"NodePoolsName","Values": ["test"]
    按照【节点池名】进行过滤。
    类型：String
    必选：否

·  "Name":"NodePoolsId","Values": ["np-d2mb2zb"]
    按照【节点池id】进行过滤。
    类型：String
    必选：否

·  "Name":"Tags","Values": ["product:tke"]
    按照【标签键值对】进行过滤。
    类型：String
    必选：否
        :type filters: list of Filter
        
        """
        req = self.model_v20180525.DescribeClusterNodePoolsRequest()
        req.ClusterId = cluster_id
        req.Filters = filters
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.DescribeClusterNodePools(req)
        return response

    @retry_with_conditions(3, 10)
    def describe_cluster_pending_releases(self, cluster_id=None, limit=None, offset=None, cluster_type=None, **kwargs):
        """在应用市场中查询正在安装中的应用列表
        :param cluster_id: 集群ID
        :type cluster_id: str
        :param limit: 返回数量限制，默认20，最大100
        :type limit: int
        :param offset: 偏移量，默认0
        :type offset: int
        :param cluster_type: 集群类型
        :type cluster_type: str
        
        """
        req = self.model_v20180525.DescribeClusterPendingReleasesRequest()
        req.ClusterId = cluster_id
        req.Limit = limit
        req.Offset = offset
        req.ClusterType = cluster_type
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.DescribeClusterPendingReleases(req)
        return response

    @retry_with_conditions(3, 10)
    def describe_cluster_release_details(self, cluster_id=None, name=None, namespace=None, cluster_type=None, **kwargs):
        """查询通过应用市场安装的某个应用详情
        :param cluster_id: 集群ID
        :type cluster_id: str
        :param name: 应用名称
        :type name: str
        :param namespace: 应用所在命名空间
        :type namespace: str
        :param cluster_type: 集群类型
        :type cluster_type: str
        
        """
        req = self.model_v20180525.DescribeClusterReleaseDetailsRequest()
        req.ClusterId = cluster_id
        req.Name = name
        req.Namespace = namespace
        req.ClusterType = cluster_type
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.DescribeClusterReleaseDetails(req)
        return response

    @retry_with_conditions(3, 10)
    def describe_cluster_release_history(self, cluster_id=None, name=None, namespace=None, cluster_type=None, **kwargs):
        """查询集群在应用市场中某个已安装应用的版本历史
        :param cluster_id: 集群ID
        :type cluster_id: str
        :param name: 应用名称
        :type name: str
        :param namespace: 应用所在命名空间
        :type namespace: str
        :param cluster_type: 集群类型
        :type cluster_type: str
        
        """
        req = self.model_v20180525.DescribeClusterReleaseHistoryRequest()
        req.ClusterId = cluster_id
        req.Name = name
        req.Namespace = namespace
        req.ClusterType = cluster_type
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.DescribeClusterReleaseHistory(req)
        return response

    @retry_with_conditions(3, 10)
    def describe_cluster_releases(self, cluster_id=None, limit=None, offset=None, cluster_type=None, namespace=None, release_name=None, chart_name=None, **kwargs):
        """查询集群在应用市场中已安装应用列表
        :param cluster_id: 集群id
        :type cluster_id: str
        :param limit: 每页数量限制
        :type limit: int
        :param offset: 页偏移量
        :type offset: int
        :param cluster_type: 集群类型, 目前支持传入 tke, eks, tkeedge, external 
        :type cluster_type: str
        :param namespace: helm Release 安装的namespace
        :type namespace: str
        :param release_name: helm Release 的名字
        :type release_name: str
        :param chart_name: helm Chart 的名字
        :type chart_name: str
        
        """
        req = self.model_v20180525.DescribeClusterReleasesRequest()
        req.ClusterId = cluster_id
        req.Limit = limit
        req.Offset = offset
        req.ClusterType = cluster_type
        req.Namespace = namespace
        req.ReleaseName = release_name
        req.ChartName = chart_name
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.DescribeClusterReleases(req)
        return response

    def describe_cluster_route_tables(self, **kwargs):
        """查询集群路由表

        :param request: Request instance for DescribeClusterRouteTables.
        :type request: :class:`tencentcloud.tke.v20180525.models.DescribeClusterRouteTablesRequest`
        :rtype: :class:`tencentcloud.tke.v20180525.models.DescribeClusterRouteTablesResponse`

        
        """
        req = self.model_v20180525.DescribeClusterRouteTablesRequest()
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.DescribeClusterRouteTables(req)
        return response

    @retry_with_conditions(3, 10)
    def describe_cluster_routes(self, route_table_name=None, filters=None, **kwargs):
        """查询集群路由
        :param route_table_name: 路由表名称。
        :type route_table_name: str
        :param filters: 过滤条件,当前只支持按照单个条件GatewayIP进行过滤（可选）
        :type filters: list of Filter
        
        """
        req = self.model_v20180525.DescribeClusterRoutesRequest()
        req.RouteTableName = route_table_name
        req.Filters = filters
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.DescribeClusterRoutes(req)
        return response

    @retry_with_conditions(3, 10)
    def describe_cluster_security(self, cluster_id=None, **kwargs):
        """集群的密钥信息
        :param cluster_id: 集群 ID，请填写 查询集群列表 接口中返回的 clusterId 字段
        :type cluster_id: str
        
        """
        req = self.model_v20180525.DescribeClusterSecurityRequest()
        req.ClusterId = cluster_id
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.DescribeClusterSecurity(req)
        return response

    @retry_with_conditions(3, 10)
    def describe_cluster_status(self, cluster_ids=None, **kwargs):
        """查看集群状态列表
        :param cluster_ids: 集群ID列表，不传默认拉取所有集群
        :type cluster_ids: list of str
        
        """
        req = self.model_v20180525.DescribeClusterStatusRequest()
        req.ClusterIds = cluster_ids
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.DescribeClusterStatus(req)
        return response

    @retry_with_conditions(3, 10)
    def describe_cluster_virtual_node(self, cluster_id=None, node_pool_id=None, node_names=None, **kwargs):
        """查看超级节点列表
        :param cluster_id: 集群ID
        :type cluster_id: str
        :param node_pool_id: 节点池ID
        :type node_pool_id: str
        :param node_names: 节点名称
        :type node_names: list of str
        
        """
        req = self.model_v20180525.DescribeClusterVirtualNodeRequest()
        req.ClusterId = cluster_id
        req.NodePoolId = node_pool_id
        req.NodeNames = node_names
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.DescribeClusterVirtualNode(req)
        return response

    @retry_with_conditions(3, 10)
    def describe_cluster_virtual_node_pools(self, cluster_id=None, **kwargs):
        """查看超级节点池列表
        :param cluster_id: 集群ID
        :type cluster_id: str
        
        """
        req = self.model_v20180525.DescribeClusterVirtualNodePoolsRequest()
        req.ClusterId = cluster_id
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.DescribeClusterVirtualNodePools(req)
        return response

    @retry_with_conditions(3, 10)
    def describe_clusters(self, cluster_ids=None, offset=None, limit=None, filters=None, cluster_type=None, **kwargs):
        """查询集群列表
        :param cluster_ids: 集群ID列表(为空时，
表示获取账号下所有集群)
        :type cluster_ids: list of str
        :param offset: 偏移量,默认0
        :type offset: int
        :param limit: 最大输出条数，默认20，最大为100
        :type limit: int
        :param filters: · "Name":"ClusterName","Values": ["test"] 按照【集群名】进行过滤。 类型：String 必选：否 · "Name":"cluster_type","Values": ["MANAGED_CLUSTER"] 按照【集群类型】进行过滤。 类型：String 必选：否 · "Name":"ClusterStatus","Values": ["Running"] 按照【集群状态】进行过滤。 类型：String 必选：否 · "Name":"vpc-id","Values": ["vpc-2wds9k9p"] 按照【VPC】进行过滤。 类型：String 必选：否 · "Name":"tag-key","Values": ["testKey"] 按照【标签键】进行过滤。 类型：String 必选：否 · "Name":"tag-value","Values": ["testValue"] 按照【标签值】进行过滤。 类型：String 必选：否 · "Name":"Tags","Values": ["product:tke"] 按照【标签键值对】进行过滤。 类型：String 必选：否
        :type filters: list of Filter
        :param cluster_type: 集群类型，例如：MANAGED_CLUSTER
        :type cluster_type: str
        
        """
        req = self.model_v20180525.DescribeClustersRequest()
        req.ClusterIds = cluster_ids
        req.Offset = offset
        req.Limit = limit
        req.Filters = filters
        req.ClusterType = cluster_type
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.DescribeClusters(req)
        return response

    @retry_with_conditions(3, 10)
    def describe_ecm_instances(self, cluster_id=None, filters=None, **kwargs):
        """获取ECM实例相关信息
        :param cluster_id: 集群id
        :type cluster_id: str
        :param filters: 过滤条件
仅支持ecm-id过滤
        :type filters: list of Filter
        
        """
        req = self.model_v20180525.DescribeECMInstancesRequest()
        req.ClusterID = cluster_id
        req.Filters = filters
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.DescribeECMInstances(req)
        return response

    @retry_with_conditions(3, 10)
    def describe_eks_cluster_credential(self, cluster_id=None, **kwargs):
        """获取弹性容器集群的接入认证信息
        :param cluster_id: 集群Id
        :type cluster_id: str
        
        """
        req = self.model_v20180525.DescribeEKSClusterCredentialRequest()
        req.ClusterId = cluster_id
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.DescribeEKSClusterCredential(req)
        return response

    @retry_with_conditions(3, 10)
    def describe_eks_clusters(self, cluster_ids=None, offset=None, limit=None, filters=None, **kwargs):
        """查询弹性集群列表
        :param cluster_ids: 集群ID列表(为空时，
表示获取账号下所有集群)
        :type cluster_ids: list of str
        :param offset: 偏移量,默认0
        :type offset: int
        :param limit: 最大输出条数，默认20
        :type limit: int
        :param filters: 过滤条件,当前只支持按照单个条件ClusterName进行过滤
        :type filters: list of Filter
        
        """
        req = self.model_v20180525.DescribeEKSClustersRequest()
        req.ClusterIds = cluster_ids
        req.Offset = offset
        req.Limit = limit
        req.Filters = filters
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.DescribeEKSClusters(req)
        return response

    @retry_with_conditions(3, 10)
    def describe_eks_container_instance_event(self, eks_ci_id=None, limit=None, **kwargs):
        """查询容器实例的事件
        :param eks_ci_id: 容器实例id
        :type eks_ci_id: str
        :param limit: 最大事件数量。默认为50，最大取值100。
        :type limit: int
        
        """
        req = self.model_v20180525.DescribeEKSContainerInstanceEventRequest()
        req.EksCiId = eks_ci_id
        req.Limit = limit
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.DescribeEKSContainerInstanceEvent(req)
        return response

    def describe_eks_container_instance_regions(self, **kwargs):
        """查询容器实例支持的地域

        :param request: Request instance for DescribeEKSContainerInstanceRegions.
        :type request: :class:`tencentcloud.tke.v20180525.models.DescribeEKSContainerInstanceRegionsRequest`
        :rtype: :class:`tencentcloud.tke.v20180525.models.DescribeEKSContainerInstanceRegionsResponse`

        
        """
        req = self.model_v20180525.DescribeEKSContainerInstanceRegionsRequest()
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.DescribeEKSContainerInstanceRegions(req)
        return response

    @retry_with_conditions(3, 10)
    def describe_eks_container_instances(self, limit=None, offset=None, filters=None, eks_ci_ids=None, **kwargs):
        """查询容器实例
        :param limit: 限定此次返回资源的数量。如果不设定，默认返回20，最大不能超过100
        :type limit: int
        :param offset: 偏移量,默认0
        :type offset: int
        :param filters: 过滤条件，可条件：
(1)实例名称
KeyName: eks-ci-name
类型：String

(2)实例状态
KeyName: status
类型：String
可选值："Pending", "Running", "Succeeded", "Failed"

(3)内网ip
KeyName: private-ip
类型：String

(4)EIP地址
KeyName: eip-address
类型：String

(5)VpcId
KeyName: vpc-id
类型：String
        :type filters: list of Filter
        :param eks_ci_ids: 容器实例 ID 数组
        :type eks_ci_ids: list of str
        
        """
        req = self.model_v20180525.DescribeEKSContainerInstancesRequest()
        req.Limit = limit
        req.Offset = offset
        req.Filters = filters
        req.EksCiIds = eks_ci_ids
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.DescribeEKSContainerInstances(req)
        return response

    @retry_with_conditions(3, 10)
    def describe_edge_available_extra_args(self, cluster_version=None, **kwargs):
        """查询边缘容器集群可用的自定义参数
        :param cluster_version: 集群版本
        :type cluster_version: str
        
        """
        req = self.model_v20180525.DescribeEdgeAvailableExtraArgsRequest()
        req.ClusterVersion = cluster_version
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.DescribeEdgeAvailableExtraArgs(req)
        return response

    @retry_with_conditions(3, 10)
    def describe_edge_cvm_instances(self, cluster_id=None, filters=None, **kwargs):
        """获取边缘容器CVM实例相关信息
        :param cluster_id: 集群id
        :type cluster_id: str
        :param filters: 过滤条件
仅支持cvm-id过滤
        :type filters: list of Filter
        
        """
        req = self.model_v20180525.DescribeEdgeCVMInstancesRequest()
        req.ClusterID = cluster_id
        req.Filters = filters
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.DescribeEdgeCVMInstances(req)
        return response

    @retry_with_conditions(3, 10)
    def describe_edge_cluster_extra_args(self, cluster_id=None, **kwargs):
        """查询边缘集群自定义参数
        :param cluster_id: 集群ID
        :type cluster_id: str
        
        """
        req = self.model_v20180525.DescribeEdgeClusterExtraArgsRequest()
        req.ClusterId = cluster_id
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.DescribeEdgeClusterExtraArgs(req)
        return response

    @retry_with_conditions(3, 10)
    def describe_edge_cluster_instances(self, cluster_id=None, limit=None, offset=None, filters=None, **kwargs):
        """查询边缘计算集群的节点信息
        :param cluster_id: 集群id
        :type cluster_id: str
        :param limit: 查询总数
        :type limit: int
        :param offset: 偏移量
        :type offset: int
        :param filters: 过滤条件，仅支持NodeName过滤
        :type filters: list of Filter
        
        """
        req = self.model_v20180525.DescribeEdgeClusterInstancesRequest()
        req.ClusterID = cluster_id
        req.Limit = limit
        req.Offset = offset
        req.Filters = filters
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.DescribeEdgeClusterInstances(req)
        return response

    @retry_with_conditions(3, 10)
    def describe_edge_cluster_upgrade_info(self, cluster_id=None, edge_version=None, **kwargs):
        """可以查询边缘集群升级信息，包含可以升级的组件，当前升级状态和升级错误信息
        :param cluster_id: 集群ID
        :type cluster_id: str
        :param edge_version: 要升级到的TKEEdge版本
        :type edge_version: str
        
        """
        req = self.model_v20180525.DescribeEdgeClusterUpgradeInfoRequest()
        req.ClusterId = cluster_id
        req.EdgeVersion = edge_version
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.DescribeEdgeClusterUpgradeInfo(req)
        return response

    @retry_with_conditions(3, 10)
    def describe_edge_log_switches(self, cluster_ids=None, **kwargs):
        """获取事件、审计和日志的状态
        :param cluster_ids: 集群ID列表
        :type cluster_ids: list of str
        
        """
        req = self.model_v20180525.DescribeEdgeLogSwitchesRequest()
        req.ClusterIds = cluster_ids
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.DescribeEdgeLogSwitches(req)
        return response

    @retry_with_conditions(3, 10)
    def describe_eks_container_instance_log(self, eks_ci_id=None, container_name=None, tail=None, start_time=None, previous=None, since_seconds=None, limit_bytes=None, **kwargs):
        """查询容器实例中容器日志
        :param eks_ci_id: Eks Container Instance Id，即容器实例Id
        :type eks_ci_id: str
        :param container_name: 容器名称，单容器的实例可选填。如果为多容器实例，请指定容器名称。
        :type container_name: str
        :param tail: 返回最新日志行数，默认500，最大2000。日志内容最大返回 1M 数据。
        :type tail: int
        :param start_time: UTC时间，RFC3339标准
        :type start_time: str
        :param previous: 是否是查上一个容器（如果容器退出重启了）
        :type previous: bool
        :param since_seconds: 查询最近多少秒内的日志
        :type since_seconds: int
        :param limit_bytes: 日志总大小限制
        :type limit_bytes: int
        
        """
        req = self.model_v20180525.DescribeEksContainerInstanceLogRequest()
        req.EksCiId = eks_ci_id
        req.ContainerName = container_name
        req.Tail = tail
        req.StartTime = start_time
        req.Previous = previous
        req.SinceSeconds = since_seconds
        req.LimitBytes = limit_bytes
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.DescribeEksContainerInstanceLog(req)
        return response

    @retry_with_conditions(3, 10)
    def describe_enable_vpc_cni_progress(self, cluster_id=None, **kwargs):
        """本接口用于查询开启vpc-cni模式的任务进度
        :param cluster_id: 开启vpc-cni的集群ID
        :type cluster_id: str
        
        """
        req = self.model_v20180525.DescribeEnableVpcCniProgressRequest()
        req.ClusterId = cluster_id
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.DescribeEnableVpcCniProgress(req)
        return response

    @retry_with_conditions(3, 10)
    def describe_encryption_status(self, cluster_id=None, **kwargs):
        """查询etcd数据是否进行加密
        :param cluster_id: 集群id
        :type cluster_id: str
        
        """
        req = self.model_v20180525.DescribeEncryptionStatusRequest()
        req.ClusterId = cluster_id
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.DescribeEncryptionStatus(req)
        return response

    @retry_with_conditions(3, 10)
    def describe_existed_instances(self, cluster_id=None, instance_ids=None, filters=None, vague_ip_address=None, vague_instance_name=None, offset=None, limit=None, ip_addresses=None, **kwargs):
        """查询已经存在的节点，判断是否可以加入集群
        :param cluster_id: 集群 ID，请填写查询集群列表 接口中返回的 cluster_id 字段（仅通过cluster_id获取需要过滤条件中的VPCID。节点状态比较时会使用该地域下所有集群中的节点进行比较。参数不支持同时指定instance_ids和cluster_id。
        :type cluster_id: str
        :param instance_ids: 按照一个或者多个实例ID查询。实例ID形如：ins-xxxxxxxx。（此参数的具体格式可参考API简介的id.N一节）。每次请求的实例的上限为100。参数不支持同时指定instance_ids和filters。
        :type instance_ids: list of str
        :param filters: 过滤条件,字段和详见[CVM查询实例](https://cloud.tencent.com/document/api/213/15728)如果设置了cluster_id，会附加集群的VPCID作为查询字段，在此情况下如果在Filter中指定了"vpc-id"作为过滤字段，指定的VPCID必须与集群的VPCID相同。
        :type filters: list of Filter
        :param vague_ip_address: 实例IP进行过滤(同时支持内网IP和外网IP)
        :type vague_ip_address: str
        :param vague_instance_name: 实例名称进行过滤
        :type vague_instance_name: str
        :param offset: 偏移量，默认为0。关于offset的更进一步介绍请参考 API [简介](https://cloud.tencent.com/document/api/213/15688)中的相关小节。
        :type offset: int
        :param limit: 返回数量，默认为20，最大值为100。关于limit的更进一步介绍请参考 API [简介](https://cloud.tencent.com/document/api/213/15688)中的相关小节。
        :type limit: int
        :param ip_addresses: 根据多个实例IP进行过滤
        :type ip_addresses: list of str
        
        """
        req = self.model_v20180525.DescribeExistedInstancesRequest()
        req.ClusterId = cluster_id
        req.InstanceIds = instance_ids
        req.Filters = filters
        req.VagueIpAddress = vague_ip_address
        req.VagueInstanceName = vague_instance_name
        req.Offset = offset
        req.Limit = limit
        req.IpAddresses = ip_addresses
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.DescribeExistedInstances(req)
        return response

    @retry_with_conditions(3, 10)
    def describe_external_node_support_config(self, cluster_id=None, **kwargs):
        """查看开启第三方节点池配置信息
        :param cluster_id: 集群Id
        :type cluster_id: str
        
        """
        req = self.model_v20180525.DescribeExternalNodeSupportConfigRequest()
        req.ClusterId = cluster_id
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.DescribeExternalNodeSupportConfig(req)
        return response

    @retry_with_conditions(3, 10)
    def describe_ipamd(self, cluster_id=None, **kwargs):
        """获取eniipamd组件信息
        :param cluster_id: 集群ID
        :type cluster_id: str
        
        """
        req = self.model_v20180525.DescribeIPAMDRequest()
        req.ClusterId = cluster_id
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.DescribeIPAMD(req)
        return response

    @retry_with_conditions(3, 10)
    def describe_image_caches(self, image_cache_ids=None, image_cache_names=None, limit=None, offset=None, filters=None, **kwargs):
        """查询镜像缓存信息接口
        :param image_cache_ids: 镜像缓存Id数组
        :type image_cache_ids: list of str
        :param image_cache_names: 镜像缓存名称数组
        :type image_cache_names: list of str
        :param limit: 限定此次返回资源的数量。如果不设定，默认返回20，最大不能超过50
        :type limit: int
        :param offset: 偏移量,默认0
        :type offset: int
        :param filters: 过滤条件，可选条件：
(1)实例名称
KeyName: image-cache-name
类型：String
        :type filters: list of Filter
        
        """
        req = self.model_v20180525.DescribeImageCachesRequest()
        req.ImageCacheIds = image_cache_ids
        req.ImageCacheNames = image_cache_names
        req.Limit = limit
        req.Offset = offset
        req.Filters = filters
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.DescribeImageCaches(req)
        return response

    def describe_images(self, **kwargs):
        """获取镜像信息

        :param request: Request instance for DescribeImages.
        :type request: :class:`tencentcloud.tke.v20180525.models.DescribeImagesRequest`
        :rtype: :class:`tencentcloud.tke.v20180525.models.DescribeImagesResponse`

        
        """
        req = self.model_v20180525.DescribeImagesRequest()
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.DescribeImages(req)
        return response

    @retry_with_conditions(3, 10)
    def describe_log_configs(self, cluster_id=None, cluster_type=None, log_config_names=None, offset=None, limit=None, **kwargs):
        """查询日志采集规则
        :param cluster_id: 集群ID
        :type cluster_id: str
        :param cluster_type: 当前集群类型支持tke、eks。默认为tke
        :type cluster_type: str
        :param log_config_names: 按照采集规则名称查找，多个采集规则使用 "," 分隔。
        :type log_config_names: str
        :param offset: 偏移量,默认0
        :type offset: int
        :param limit: 最大输出条数，默认20，最大为100
        :type limit: int
        
        """
        req = self.model_v20180525.DescribeLogConfigsRequest()
        req.ClusterId = cluster_id
        req.ClusterType = cluster_type
        req.LogConfigNames = log_config_names
        req.Offset = offset
        req.Limit = limit
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.DescribeLogConfigs(req)
        return response

    @retry_with_conditions(3, 10)
    def describe_log_switches(self, cluster_ids=None, cluster_type=None, **kwargs):
        """查询集群日志（审计、事件、普通日志）开关列表
        :param cluster_ids: 集群ID列表
        :type cluster_ids: list of str
        :param cluster_type: 集群类型，tke 或eks
        :type cluster_type: str
        
        """
        req = self.model_v20180525.DescribeLogSwitchesRequest()
        req.ClusterIds = cluster_ids
        req.ClusterType = cluster_type
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.DescribeLogSwitches(req)
        return response

    def describe_os_images(self, **kwargs):
        """获取OS聚合信息

        :param request: Request instance for DescribeOSImages.
        :type request: :class:`tencentcloud.tke.v20180525.models.DescribeOSImagesRequest`
        :rtype: :class:`tencentcloud.tke.v20180525.models.DescribeOSImagesResponse`

        
        """
        req = self.model_v20180525.DescribeOSImagesRequest()
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.DescribeOSImages(req)
        return response

    @retry_with_conditions(3, 10)
    def describe_open_policy_list(self, cluster_id=None, category=None, **kwargs):
        """查询opa策略列表
        :param cluster_id: 集群ID
        :type cluster_id: str
        :param category: 策略分类 基线：baseline 优选：priority 可选：optional
        :type category: str
        
        """
        req = self.model_v20180525.DescribeOpenPolicyListRequest()
        req.ClusterId = cluster_id
        req.Category = category
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.DescribeOpenPolicyList(req)
        return response

    @retry_with_conditions(3, 10)
    def describe_pod_charge_info(self, cluster_id=None, namespace=None, name=None, uids=None, **kwargs):
        """查询正在运行中Pod的计费信息。可以通过 Namespace 和 Name 来查询某个 Pod 的信息，也可以通过 Pod 的 Uid 批量查询。
        :param cluster_id: 集群ID
        :type cluster_id: str
        :param namespace: 命名空间
        :type namespace: str
        :param name: Pod名称
        :type name: str
        :param uids: Pod的Uid
        :type uids: list of str
        
        """
        req = self.model_v20180525.DescribePodChargeInfoRequest()
        req.ClusterId = cluster_id
        req.Namespace = namespace
        req.Name = name
        req.Uids = uids
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.DescribePodChargeInfo(req)
        return response

    @retry_with_conditions(3, 10)
    def describe_pod_deduction_rate(self, zone=None, cluster_id=None, node_name=None, **kwargs):
        """查询各个规格的 Pod 的抵扣率
        :param zone: 可用区
        :type zone: str
        :param cluster_id: 集群 ID
        :type cluster_id: str
        :param node_name:  节点名称
        :type node_name: str
        
        """
        req = self.model_v20180525.DescribePodDeductionRateRequest()
        req.Zone = zone
        req.ClusterId = cluster_id
        req.NodeName = node_name
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.DescribePodDeductionRate(req)
        return response

    @retry_with_conditions(3, 10)
    def describe_pods_by_spec(self, cpu=None, memory=None, gpu_num=None, zone=None, cluster_id=None, node_name=None, offset=None, limit=None, filters=None, **kwargs):
        """查询可以用预留券抵扣的 Pod 信息。
        :param cpu: 核数
        :type cpu: float
        :param memory: 内存
        :type memory: float
        :param gpu_num: 卡数，有0.25、0.5、1、2、4等
        :type gpu_num: str
        :param zone: 可用区
        :type zone: str
        :param cluster_id: 集群 ID
        :type cluster_id: str
        :param node_name: 节点名称
        :type node_name: str
        :param offset: 偏移量，默认0。
        :type offset: int
        :param limit: 返回数量，默认为20，最大值为100。
        :type limit: int
        :param filters: pod-type
按照**【Pod 类型**】进行过滤。资源类型：intel、amd、v100、t4、a10\*gnv4、a10\*gnv4v等。
类型：String
必选：否

pod-deduct
按照**【上个周期抵扣的Pod**】进行过滤。Values可不设置。
必选：否

pod-not-deduct
按照**【上个周期未抵扣的Pod**】进行过滤。Values可不设置。
必选：否
        :type filters: list of Filter
        
        """
        req = self.model_v20180525.DescribePodsBySpecRequest()
        req.Cpu = cpu
        req.Memory = memory
        req.GpuNum = gpu_num
        req.Zone = zone
        req.ClusterId = cluster_id
        req.NodeName = node_name
        req.Offset = offset
        req.Limit = limit
        req.Filters = filters
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.DescribePodsBySpec(req)
        return response

    @retry_with_conditions(3, 10)
    def describe_post_node_resources(self, cluster_id=None, node_name=None, **kwargs):
        """包括 Pod 资源统计和绑定的预留券资源统计。
        :param cluster_id: 集群 ID
        :type cluster_id: str
        :param node_name:  节点名称
        :type node_name: str
        
        """
        req = self.model_v20180525.DescribePostNodeResourcesRequest()
        req.ClusterId = cluster_id
        req.NodeName = node_name
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.DescribePostNodeResources(req)
        return response

    @retry_with_conditions(3, 10)
    def describe_prometheus_agent_instances(self, cluster_id=None, **kwargs):
        """获取关联目标集群的实例列表
        :param cluster_id: 集群id
可以是tke, eks, edge的集群id
        :type cluster_id: str
        
        """
        req = self.model_v20180525.DescribePrometheusAgentInstancesRequest()
        req.ClusterId = cluster_id
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.DescribePrometheusAgentInstances(req)
        return response

    @retry_with_conditions(3, 10)
    def describe_prometheus_agents(self, instance_id=None, offset=None, limit=None, **kwargs):
        """获取被关联集群列表
        :param instance_id: 实例id
        :type instance_id: str
        :param offset: 用于分页
        :type offset: int
        :param limit: 用于分页
        :type limit: int
        
        """
        req = self.model_v20180525.DescribePrometheusAgentsRequest()
        req.InstanceId = instance_id
        req.Offset = offset
        req.Limit = limit
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.DescribePrometheusAgents(req)
        return response

    @retry_with_conditions(3, 10)
    def describe_prometheus_alert_history(self, instance_id=None, rule_name=None, start_time=None, end_time=None, labels=None, offset=None, limit=None, **kwargs):
        """获取告警历史
        :param instance_id: 实例id
        :type instance_id: str
        :param rule_name: 告警名称
        :type rule_name: str
        :param start_time: 开始时间
        :type start_time: str
        :param end_time: 结束时间
        :type end_time: str
        :param labels: label集合
        :type labels: str
        :param offset: 分片
        :type offset: int
        :param limit: 分片
        :type limit: int
        
        """
        req = self.model_v20180525.DescribePrometheusAlertHistoryRequest()
        req.InstanceId = instance_id
        req.RuleName = rule_name
        req.StartTime = start_time
        req.EndTime = end_time
        req.Labels = labels
        req.Offset = offset
        req.Limit = limit
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.DescribePrometheusAlertHistory(req)
        return response

    @retry_with_conditions(3, 10)
    def describe_prometheus_alert_policy(self, instance_id=None, offset=None, limit=None, filters=None, **kwargs):
        """获取2.0实例告警策略列表
        :param instance_id: 实例id
        :type instance_id: str
        :param offset: 分页
        :type offset: int
        :param limit: 分页
        :type limit: int
        :param filters: 过滤
支持ID，Name
        :type filters: list of Filter
        
        """
        req = self.model_v20180525.DescribePrometheusAlertPolicyRequest()
        req.InstanceId = instance_id
        req.Offset = offset
        req.Limit = limit
        req.Filters = filters
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.DescribePrometheusAlertPolicy(req)
        return response

    @retry_with_conditions(3, 10)
    def describe_prometheus_alert_rule(self, instance_id=None, offset=None, limit=None, filters=None, **kwargs):
        """获取告警规则列表
        :param instance_id: 实例id
        :type instance_id: str
        :param offset: 分页
        :type offset: int
        :param limit: 分页
        :type limit: int
        :param filters: 过滤
支持ID，Name
        :type filters: list of Filter
        
        """
        req = self.model_v20180525.DescribePrometheusAlertRuleRequest()
        req.InstanceId = instance_id
        req.Offset = offset
        req.Limit = limit
        req.Filters = filters
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.DescribePrometheusAlertRule(req)
        return response

    @retry_with_conditions(3, 10)
    def describe_prometheus_cluster_agents(self, instance_id=None, offset=None, limit=None, **kwargs):
        """获取TMP实例关联集群列表
        :param instance_id: 实例id
        :type instance_id: str
        :param offset: 用于分页
        :type offset: int
        :param limit: 用于分页
        :type limit: int
        
        """
        req = self.model_v20180525.DescribePrometheusClusterAgentsRequest()
        req.InstanceId = instance_id
        req.Offset = offset
        req.Limit = limit
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.DescribePrometheusClusterAgents(req)
        return response

    @retry_with_conditions(3, 10)
    def describe_prometheus_config(self, instance_id=None, cluster_id=None, cluster_type=None, **kwargs):
        """获取集群采集配置
        :param instance_id: 实例id
        :type instance_id: str
        :param cluster_id: 集群id
        :type cluster_id: str
        :param cluster_type: 集群类型
        :type cluster_type: str
        
        """
        req = self.model_v20180525.DescribePrometheusConfigRequest()
        req.InstanceId = instance_id
        req.ClusterId = cluster_id
        req.ClusterType = cluster_type
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.DescribePrometheusConfig(req)
        return response

    @retry_with_conditions(3, 10)
    def describe_prometheus_global_config(self, instance_id=None, disable_statistics=None, **kwargs):
        """获得实例级别抓取配置
        :param instance_id: 实例级别抓取配置
        :type instance_id: str
        :param disable_statistics: 是否禁用统计
        :type disable_statistics: bool
        
        """
        req = self.model_v20180525.DescribePrometheusGlobalConfigRequest()
        req.InstanceId = instance_id
        req.DisableStatistics = disable_statistics
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.DescribePrometheusGlobalConfig(req)
        return response

    @retry_with_conditions(3, 10)
    def describe_prometheus_global_notification(self, instance_id=None, **kwargs):
        """查询全局告警通知渠道
        :param instance_id: 实例ID
        :type instance_id: str
        
        """
        req = self.model_v20180525.DescribePrometheusGlobalNotificationRequest()
        req.InstanceId = instance_id
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.DescribePrometheusGlobalNotification(req)
        return response

    @retry_with_conditions(3, 10)
    def describe_prometheus_instance(self, instance_id=None, **kwargs):
        """获取实例详细信息
        :param instance_id: 实例id
        :type instance_id: str
        
        """
        req = self.model_v20180525.DescribePrometheusInstanceRequest()
        req.InstanceId = instance_id
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.DescribePrometheusInstance(req)
        return response

    @retry_with_conditions(3, 10)
    def describe_prometheus_instance_init_status(self, instance_id=None, **kwargs):
        """获取2.0实例初始化任务状态
        :param instance_id: 实例ID
        :type instance_id: str
        
        """
        req = self.model_v20180525.DescribePrometheusInstanceInitStatusRequest()
        req.InstanceId = instance_id
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.DescribePrometheusInstanceInitStatus(req)
        return response

    @retry_with_conditions(3, 10)
    def describe_prometheus_instances_overview(self, offset=None, limit=None, filters=None, **kwargs):
        """获取与云监控融合实例列表
        :param offset: 用于分页
        :type offset: int
        :param limit: 用于分页
        :type limit: int
        :param filters: 过滤实例，目前支持：
ID: 通过实例ID来过滤 
Name: 通过实例名称来过滤
        :type filters: list of Filter
        
        """
        req = self.model_v20180525.DescribePrometheusInstancesOverviewRequest()
        req.Offset = offset
        req.Limit = limit
        req.Filters = filters
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.DescribePrometheusInstancesOverview(req)
        return response

    @retry_with_conditions(3, 10)
    def describe_prometheus_overviews(self, offset=None, limit=None, filters=None, **kwargs):
        """获取实例列表
        :param offset: 用于分页
        :type offset: int
        :param limit: 用于分页
        :type limit: int
        :param filters: 过滤实例，目前支持：
ID: 通过实例ID来过滤 
Name: 通过实例名称来过滤
        :type filters: list of Filter
        
        """
        req = self.model_v20180525.DescribePrometheusOverviewsRequest()
        req.Offset = offset
        req.Limit = limit
        req.Filters = filters
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.DescribePrometheusOverviews(req)
        return response

    @retry_with_conditions(3, 10)
    def describe_prometheus_record_rules(self, instance_id=None, offset=None, limit=None, filters=None, **kwargs):
        """获取聚合规则列表，包含关联集群内crd资源创建的record rule
        :param instance_id: 实例id
        :type instance_id: str
        :param offset: 分页
        :type offset: int
        :param limit: 分页
        :type limit: int
        :param filters: 过滤
        :type filters: list of Filter
        
        """
        req = self.model_v20180525.DescribePrometheusRecordRulesRequest()
        req.InstanceId = instance_id
        req.Offset = offset
        req.Limit = limit
        req.Filters = filters
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.DescribePrometheusRecordRules(req)
        return response

    @retry_with_conditions(3, 10)
    def describe_prometheus_targets(self, instance_id=None, cluster_type=None, cluster_id=None, filters=None, **kwargs):
        """获取targets信息
        :param instance_id: 实例id
        :type instance_id: str
        :param cluster_type: 集群类型
        :type cluster_type: str
        :param cluster_id: 集群id
        :type cluster_id: str
        :param filters: 过滤条件，当前支持
Name=state
Value=up, down, unknown
        :type filters: list of Filter
        
        """
        req = self.model_v20180525.DescribePrometheusTargetsRequest()
        req.InstanceId = instance_id
        req.ClusterType = cluster_type
        req.ClusterId = cluster_id
        req.Filters = filters
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.DescribePrometheusTargets(req)
        return response

    @retry_with_conditions(3, 10)
    def describe_prometheus_temp(self, filters=None, offset=None, limit=None, **kwargs):
        """拉取模板列表，默认模板将总是在最前面
        :param filters: 模糊过滤条件，支持
Level 按模板级别过滤
Name 按名称过滤
Describe 按描述过滤
ID 按templateId过滤
        :type filters: list of Filter
        :param offset: 分页偏移
        :type offset: int
        :param limit: 总数限制
        :type limit: int
        
        """
        req = self.model_v20180525.DescribePrometheusTempRequest()
        req.Filters = filters
        req.Offset = offset
        req.Limit = limit
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.DescribePrometheusTemp(req)
        return response

    @retry_with_conditions(3, 10)
    def describe_prometheus_temp_sync(self, template_id=None, **kwargs):
        """获取模板关联实例信息，针对V2版本实例
        :param template_id: 模板ID
        :type template_id: str
        
        """
        req = self.model_v20180525.DescribePrometheusTempSyncRequest()
        req.TemplateId = template_id
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.DescribePrometheusTempSync(req)
        return response

    @retry_with_conditions(3, 10)
    def describe_prometheus_template_sync(self, template_id=None, **kwargs):
        """获取模板同步信息
        :param template_id: 模板ID
        :type template_id: str
        
        """
        req = self.model_v20180525.DescribePrometheusTemplateSyncRequest()
        req.TemplateId = template_id
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.DescribePrometheusTemplateSync(req)
        return response

    @retry_with_conditions(3, 10)
    def describe_prometheus_templates(self, filters=None, offset=None, limit=None, **kwargs):
        """拉取模板列表，默认模板将总是在最前面
        :param filters: 模糊过滤条件，支持
Level 按模板级别过滤
Name 按名称过滤
Describe 按描述过滤
ID 按templateId过滤
        :type filters: list of Filter
        :param offset: 分页偏移
        :type offset: int
        :param limit: 总数限制
        :type limit: int
        
        """
        req = self.model_v20180525.DescribePrometheusTemplatesRequest()
        req.Filters = filters
        req.Offset = offset
        req.Limit = limit
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.DescribePrometheusTemplates(req)
        return response

    @retry_with_conditions(3, 10)
    def describe_ri_utilization_detail(self, offset=None, limit=None, filters=None, **kwargs):
        """预留实例用量查询
        :param offset: 偏移量，默认0。
        :type offset: int
        :param limit: 返回数量，默认为20，最大值为100。
        :type limit: int
        :param filters: reserved-instance-id
按照**【预留实例ID**】进行过滤。预留实例ID形如：eksri-xxxxxxxx。
类型：String
必选：否

begin-time
按照**【抵扣开始时间**】进行过滤。形如：2023-06-28 15:27:40。
类型：String
必选：否

end-time
按照**【抵扣结束时间**】进行过滤。形如：2023-06-28 15:27:40。
类型：String
必选：否
        :type filters: list of Filter
        
        """
        req = self.model_v20180525.DescribeRIUtilizationDetailRequest()
        req.Offset = offset
        req.Limit = limit
        req.Filters = filters
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.DescribeRIUtilizationDetail(req)
        return response

    def describe_regions(self, **kwargs):
        """获取容器服务支持的所有地域

        :param request: Request instance for DescribeRegions.
        :type request: :class:`tencentcloud.tke.v20180525.models.DescribeRegionsRequest`
        :rtype: :class:`tencentcloud.tke.v20180525.models.DescribeRegionsResponse`

        
        """
        req = self.model_v20180525.DescribeRegionsRequest()
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.DescribeRegions(req)
        return response

    @retry_with_conditions(3, 10)
    def describe_reserved_instance_utilization_rate(self, zone=None, cluster_id=None, node_name=None, **kwargs):
        """查询各种规格类型的预留券使用率
        :param zone: 可用区
        :type zone: str
        :param cluster_id: 集群 ID
        :type cluster_id: str
        :param node_name:  节点名称
        :type node_name: str
        
        """
        req = self.model_v20180525.DescribeReservedInstanceUtilizationRateRequest()
        req.Zone = zone
        req.ClusterId = cluster_id
        req.NodeName = node_name
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.DescribeReservedInstanceUtilizationRate(req)
        return response

    @retry_with_conditions(3, 10)
    def describe_reserved_instances(self, offset=None, limit=None, filters=None, order_field=None, order_direction=None, **kwargs):
        """查询预留实例列表
        :param offset: 偏移量，默认0。
        :type offset: int
        :param limit: 返回数量，默认为20，最大值为100。
        :type limit: int
        :param filters: status
按照**【状态**】进行过滤。状态：Creating、Active、Expired、Refunded。
类型：String
必选：否

resource-type
按照**【资源类型**】进行过滤。资源类型：common、amd、v100、t4、a10\*gnv4、a10\*gnv4v等，common表示通用类型。
类型：String
必选：否

cpu
按照**【核数**】进行过滤。
类型：String
必选：否

memory
按照**【内存**】进行过滤。
类型：String
必选：否

gpu
按照**【GPU卡数**】进行过滤，取值有0.25、0.5、1、2、4等。
类型：String
必选：否

cluster-id
按照**【集群ID**】进行过滤。
类型：String
必选：否

node-name
按照**【节点名称**】进行过滤。
类型：String
必选：否

scope
按照**【可用区**】进行过滤。比如：ap-guangzhou-2，为空字符串表示地域抵扣范围。如果只过滤可用区抵扣范围，需要同时将cluster-id、node-name设置为空字符串。
类型：String
必选：否

reserved-instance-id
按照**【预留实例ID**】进行过滤。预留实例ID形如：eksri-xxxxxxxx。
类型：String
必选：否

reserved-instance-name
按照**【预留实例名称**】进行过滤。
类型：String
必选：否

reserved-instance-deduct
按照**【上个周期抵扣的预留券**】进行过滤。Values可不设置。
必选：否

reserved-instance-not-deduct
按照**【上个周期未抵扣的预留券**】进行过滤。Values可不设置。
必选：否
        :type filters: list of Filter
        :param order_field: 排序字段。支持CreatedAt、ActiveAt、ExpireAt。默认值CreatedAt。
        :type order_field: str
        :param order_direction: 排序方法。顺序：ASC，倒序：DESC。默认值DESC。
        :type order_direction: str
        
        """
        req = self.model_v20180525.DescribeReservedInstancesRequest()
        req.Offset = offset
        req.Limit = limit
        req.Filters = filters
        req.OrderField = order_field
        req.OrderDirection = order_direction
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.DescribeReservedInstances(req)
        return response

    @retry_with_conditions(3, 10)
    def describe_resource_usage(self, cluster_id=None, **kwargs):
        """获取集群资源使用量
        :param cluster_id: 集群ID
        :type cluster_id: str
        
        """
        req = self.model_v20180525.DescribeResourceUsageRequest()
        req.ClusterId = cluster_id
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.DescribeResourceUsage(req)
        return response

    @retry_with_conditions(3, 10)
    def describe_route_table_conflicts(self, route_table_cidr_block=None, vpc_id=None, **kwargs):
        """查询路由表冲突列表
        :param route_table_cidr_block: 路由表CIDR
        :type route_table_cidr_block: str
        :param vpc_id: 路由表绑定的VPC
        :type vpc_id: str
        
        """
        req = self.model_v20180525.DescribeRouteTableConflictsRequest()
        req.RouteTableCidrBlock = route_table_cidr_block
        req.VpcId = vpc_id
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.DescribeRouteTableConflicts(req)
        return response

    @retry_with_conditions(3, 10)
    def describe_supported_runtime(self, k8s_version=None, **kwargs):
        """根据K8S版本获取可选运行时版本
        :param k8s_version: K8S版本
        :type k8s_version: str
        
        """
        req = self.model_v20180525.DescribeSupportedRuntimeRequest()
        req.K8sVersion = k8s_version
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.DescribeSupportedRuntime(req)
        return response

    @retry_with_conditions(3, 10)
    def describe_tke_edge_cluster_credential(self, cluster_id=None, **kwargs):
        """获取边缘计算集群的认证信息
        :param cluster_id: 集群Id
        :type cluster_id: str
        
        """
        req = self.model_v20180525.DescribeTKEEdgeClusterCredentialRequest()
        req.ClusterId = cluster_id
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.DescribeTKEEdgeClusterCredential(req)
        return response

    @retry_with_conditions(3, 10)
    def describe_tke_edge_cluster_status(self, cluster_id=None, **kwargs):
        """获取边缘计算集群的当前状态以及过程信息
        :param cluster_id: 边缘计算容器集群Id
        :type cluster_id: str
        
        """
        req = self.model_v20180525.DescribeTKEEdgeClusterStatusRequest()
        req.ClusterId = cluster_id
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.DescribeTKEEdgeClusterStatus(req)
        return response

    @retry_with_conditions(3, 10)
    def describe_tke_edge_clusters(self, cluster_ids=None, offset=None, limit=None, filters=None, **kwargs):
        """查询边缘集群列表
        :param cluster_ids: 集群ID列表(为空时，
表示获取账号下所有集群)
        :type cluster_ids: list of str
        :param offset: 偏移量,默认0
        :type offset: int
        :param limit: 最大输出条数，默认20
        :type limit: int
        :param filters: 过滤条件,当前只支持按照ClusterName和云标签进行过滤,云标签过滤格式Tags:["key1:value1","key2:value2"]
        :type filters: list of Filter
        
        """
        req = self.model_v20180525.DescribeTKEEdgeClustersRequest()
        req.ClusterIds = cluster_ids
        req.Offset = offset
        req.Limit = limit
        req.Filters = filters
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.DescribeTKEEdgeClusters(req)
        return response

    @retry_with_conditions(3, 10)
    def describe_tke_edge_external_kubeconfig(self, cluster_id=None, **kwargs):
        """获取边缘计算外部访问的kubeconfig
        :param cluster_id: 集群id
        :type cluster_id: str
        
        """
        req = self.model_v20180525.DescribeTKEEdgeExternalKubeconfigRequest()
        req.ClusterId = cluster_id
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.DescribeTKEEdgeExternalKubeconfig(req)
        return response

    @retry_with_conditions(3, 10)
    def describe_tke_edge_script(self, cluster_id=None, interface=None, node_name=None, config=None, script_version=None, **kwargs):
        """获取边缘脚本链接，此接口用于添加第三方节点，通过下载脚本从而将节点添加到边缘集群。
        :param cluster_id: 集群id
        :type cluster_id: str
        :param interface: 网卡名,指定边缘节点上kubelet向apiserver注册使用的网卡
        :type interface: str
        :param node_name: 节点名字
        :type node_name: str
        :param config: json格式的节点配置
        :type config: str
        :param script_version: 可以下载某个历史版本的edgectl脚本，默认下载最新版本，edgectl版本信息可以在脚本里查看
        :type script_version: str
        
        """
        req = self.model_v20180525.DescribeTKEEdgeScriptRequest()
        req.ClusterId = cluster_id
        req.Interface = interface
        req.NodeName = node_name
        req.Config = config
        req.ScriptVersion = script_version
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.DescribeTKEEdgeScript(req)
        return response

    def describe_versions(self, **kwargs):
        """获取集群版本信息

        :param request: Request instance for DescribeVersions.
        :type request: :class:`tencentcloud.tke.v20180525.models.DescribeVersionsRequest`
        :rtype: :class:`tencentcloud.tke.v20180525.models.DescribeVersionsResponse`

        
        """
        req = self.model_v20180525.DescribeVersionsRequest()
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.DescribeVersions(req)
        return response

    @retry_with_conditions(3, 10)
    def describe_vpc_cni_pod_limits(self, zone=None, instance_family=None, instance_type=None, **kwargs):
        """本接口查询当前用户和地域在指定可用区下的机型可支持的最大 TKE VPC-CNI 网络模式的 Pod 数量
        :param zone: 查询的机型所在可用区，如：ap-guangzhou-3，默认为空，即不按可用区过滤信息
        :type zone: str
        :param instance_family: 查询的实例机型系列信息，如：S5，默认为空，即不按机型系列过滤信息
        :type instance_family: str
        :param instance_type: 查询的实例机型信息，如：S5.LARGE8，默认为空，即不按机型过滤信息
        :type instance_type: str
        
        """
        req = self.model_v20180525.DescribeVpcCniPodLimitsRequest()
        req.Zone = zone
        req.InstanceFamily = instance_family
        req.InstanceType = instance_type
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.DescribeVpcCniPodLimits(req)
        return response

    @retry_with_conditions(3, 10)
    def disable_cluster_audit(self, cluster_id=None, delete_log_set_and_topic=None, **kwargs):
        """关闭集群审计
        :param cluster_id: 集群ID
        :type cluster_id: str
        :param delete_log_set_and_topic: 取值为true代表关闭集群审计时删除默认创建的日志集和主题，false代表不删除
        :type delete_log_set_and_topic: bool
        
        """
        req = self.model_v20180525.DisableClusterAuditRequest()
        req.ClusterId = cluster_id
        req.DeleteLogSetAndTopic = delete_log_set_and_topic
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.DisableClusterAudit(req)
        return response

    @retry_with_conditions(3, 10)
    def disable_cluster_deletion_protection(self, cluster_id=None, **kwargs):
        """关闭集群删除保护
        :param cluster_id: 集群ID
        :type cluster_id: str
        
        """
        req = self.model_v20180525.DisableClusterDeletionProtectionRequest()
        req.ClusterId = cluster_id
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.DisableClusterDeletionProtection(req)
        return response

    @retry_with_conditions(3, 10)
    def disable_encryption_protection(self, cluster_id=None, **kwargs):
        """关闭加密信息保护
        :param cluster_id: 集群ID
        :type cluster_id: str
        
        """
        req = self.model_v20180525.DisableEncryptionProtectionRequest()
        req.ClusterId = cluster_id
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.DisableEncryptionProtection(req)
        return response

    @retry_with_conditions(3, 10)
    def disable_event_persistence(self, cluster_id=None, delete_log_set_and_topic=None, **kwargs):
        """关闭事件持久化功能
        :param cluster_id: 集群ID
        :type cluster_id: str
        :param delete_log_set_and_topic: 取值为true代表关闭集群审计时删除默认创建的日志集和主题，false代表不删除
        :type delete_log_set_and_topic: bool
        
        """
        req = self.model_v20180525.DisableEventPersistenceRequest()
        req.ClusterId = cluster_id
        req.DeleteLogSetAndTopic = delete_log_set_and_topic
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.DisableEventPersistence(req)
        return response

    @retry_with_conditions(3, 10)
    def disable_vpc_cni_network_type(self, cluster_id=None, **kwargs):
        """提供给附加了VPC-CNI能力的Global-Route集群关闭VPC-CNI
        :param cluster_id: 集群ID
        :type cluster_id: str
        
        """
        req = self.model_v20180525.DisableVpcCniNetworkTypeRequest()
        req.ClusterId = cluster_id
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.DisableVpcCniNetworkType(req)
        return response

    @retry_with_conditions(3, 10)
    def drain_cluster_virtual_node(self, cluster_id=None, node_name=None, **kwargs):
        """驱逐超级节点
        :param cluster_id: 集群ID
        :type cluster_id: str
        :param node_name: 节点名
        :type node_name: str
        
        """
        req = self.model_v20180525.DrainClusterVirtualNodeRequest()
        req.ClusterId = cluster_id
        req.NodeName = node_name
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.DrainClusterVirtualNode(req)
        return response

    @retry_with_conditions(3, 10)
    def enable_cluster_audit(self, cluster_id=None, logset_id=None, topic_id=None, topic_region=None, **kwargs):
        """开启集群审计
        :param cluster_id: 集群ID
        :type cluster_id: str
        :param logset_id: CLS日志集ID
        :type logset_id: str
        :param topic_id: CLS日志主题ID
        :type topic_id: str
        :param topic_region: topic所在region，默认为集群当前region
        :type topic_region: str
        
        """
        req = self.model_v20180525.EnableClusterAuditRequest()
        req.ClusterId = cluster_id
        req.LogsetId = logset_id
        req.TopicId = topic_id
        req.TopicRegion = topic_region
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.EnableClusterAudit(req)
        return response

    @retry_with_conditions(3, 10)
    def enable_cluster_deletion_protection(self, cluster_id=None, **kwargs):
        """启用集群删除保护
        :param cluster_id: 集群ID
        :type cluster_id: str
        
        """
        req = self.model_v20180525.EnableClusterDeletionProtectionRequest()
        req.ClusterId = cluster_id
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.EnableClusterDeletionProtection(req)
        return response

    @retry_with_conditions(3, 10)
    def enable_encryption_protection(self, cluster_id=None, kms_configuration=None, **kwargs):
        """开启加密数据保护，需要先开启KMS能力，完成KMS授权
        :param cluster_id: 集群ID
        :type cluster_id: str
        :param kms_configuration: kms加密配置
        :type kms_configuration: :class:`tencentcloud.tke.v20180525.models.kms_configuration`
        
        """
        req = self.model_v20180525.EnableEncryptionProtectionRequest()
        req.ClusterId = cluster_id
        req.KMSConfiguration = kms_configuration
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.EnableEncryptionProtection(req)
        return response

    @retry_with_conditions(3, 10)
    def enable_event_persistence(self, cluster_id=None, logset_id=None, topic_id=None, topic_region=None, **kwargs):
        """开启事件持久化功能
        :param cluster_id: 集群ID
        :type cluster_id: str
        :param logset_id: cls服务的logsetID
        :type logset_id: str
        :param topic_id: cls服务的topicID
        :type topic_id: str
        :param topic_region: topic所在地域，默认为集群所在地域
        :type topic_region: str
        
        """
        req = self.model_v20180525.EnableEventPersistenceRequest()
        req.ClusterId = cluster_id
        req.LogsetId = logset_id
        req.TopicId = topic_id
        req.TopicRegion = topic_region
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.EnableEventPersistence(req)
        return response

    @retry_with_conditions(3, 10)
    def enable_vpc_cni_network_type(self, cluster_id=None, vpc_cni_type=None, enable_static_ip=None, subnets=None, expired_seconds=None, skip_adding_non_masquerade_cid_rs=None, **kwargs):
        """GR集群可以通过本接口附加vpc-cni容器网络插件，开启vpc-cni容器网络能力
        :param cluster_id: 集群ID
        :type cluster_id: str
        :param vpc_cni_type: 开启vpc-cni的模式，tke-route-eni开启的是策略路由模式，tke-direct-eni开启的是独立网卡模式
        :type vpc_cni_type: str
        :param enable_static_ip: 是否开启固定IP模式
        :type enable_static_ip: bool
        :param subnets: 使用的容器子网
        :type subnets: list of str
        :param expired_seconds: 在固定IP模式下，Pod销毁后退还IP的时间，传参必须大于300；不传默认IP永不销毁。
        :type expired_seconds: int
        :param skip_adding_non_masquerade_cid_rs: 是否同步添加 vpc 网段到 ip-masq-agent-config 的 NonMasqueradeCIDRs 字段，默认 false 会同步添加
        :type skip_adding_non_masquerade_cid_rs: bool
        
        """
        req = self.model_v20180525.EnableVpcCniNetworkTypeRequest()
        req.ClusterId = cluster_id
        req.VpcCniType = vpc_cni_type
        req.EnableStaticIp = enable_static_ip
        req.Subnets = subnets
        req.ExpiredSeconds = expired_seconds
        req.SkipAddingNonMasqueradeCIDRs = skip_adding_non_masquerade_cid_rs
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.EnableVpcCniNetworkType(req)
        return response

    @retry_with_conditions(3, 10)
    def forward_application_request_v3(self, method=None, path=None, accept=None, content_type=None, request_body=None, cluster_name=None, encoded_body=None, **kwargs):
        """操作TKE集群的addon
        :param method: 请求集群addon的访问
        :type method: str
        :param path: 请求集群addon的路径
        :type path: str
        :param accept: 请求集群addon后允许接收的数据格式
        :type accept: str
        :param content_type: 请求集群addon的数据格式
        :type content_type: str
        :param request_body: 请求集群addon的数据
        :type request_body: str
        :param cluster_name: 集群名称
        :type cluster_name: str
        :param encoded_body: 是否编码请求内容
        :type encoded_body: str
        
        """
        req = self.model_v20180525.ForwardApplicationRequestV3Request()
        req.Method = method
        req.Path = path
        req.Accept = accept
        req.ContentType = content_type
        req.RequestBody = request_body
        req.ClusterName = cluster_name
        req.EncodedBody = encoded_body
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.ForwardApplicationRequestV3(req)
        return response

    @retry_with_conditions(3, 10)
    def forward_tke_edge_application_request_v3(self, method=None, path=None, accept=None, content_type=None, request_body=None, cluster_name=None, encoded_body=None, **kwargs):
        """操作TKEEdge集群的addon
        :param method: 请求集群addon的访问
        :type method: str
        :param path: 请求集群addon的路径
        :type path: str
        :param accept: 请求集群addon后允许接收的数据格式
        :type accept: str
        :param content_type: 请求集群addon的数据格式
        :type content_type: str
        :param request_body: 请求集群addon的数据
        :type request_body: str
        :param cluster_name: 集群名称，例如cls-1234abcd
        :type cluster_name: str
        :param encoded_body: 是否编码请求内容
        :type encoded_body: str
        
        """
        req = self.model_v20180525.ForwardTKEEdgeApplicationRequestV3Request()
        req.Method = method
        req.Path = path
        req.Accept = accept
        req.ContentType = content_type
        req.RequestBody = request_body
        req.ClusterName = cluster_name
        req.EncodedBody = encoded_body
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.ForwardTKEEdgeApplicationRequestV3(req)
        return response

    @retry_with_conditions(3, 10)
    def get_cluster_level_price(self, cluster_level=None, **kwargs):
        """获取集群规模价格
        :param cluster_level: 集群规格，托管集群询价
        :type cluster_level: str
        
        """
        req = self.model_v20180525.GetClusterLevelPriceRequest()
        req.ClusterLevel = cluster_level
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.GetClusterLevelPrice(req)
        return response

    @retry_with_conditions(3, 10)
    def get_most_suitable_image_cache(self, images=None, **kwargs):
        """根据镜像列表，查询匹配的镜像缓存
        :param images: 容器镜像列表
        :type images: list of str
        
        """
        req = self.model_v20180525.GetMostSuitableImageCacheRequest()
        req.Images = images
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.GetMostSuitableImageCache(req)
        return response

    @retry_with_conditions(3, 10)
    def get_tke_app_chart_list(self, kind=None, arch=None, cluster_type=None, **kwargs):
        """获取TKE支持的App列表
        :param kind: app类型，取值log,scheduler,network,storage,monitor,dns,image,other,invisible
        :type kind: str
        :param arch: app支持的操作系统，取值arm32、arm64、amd64
        :type arch: str
        :param cluster_type: 集群类型，取值tke、eks
        :type cluster_type: str
        
        """
        req = self.model_v20180525.GetTkeAppChartListRequest()
        req.Kind = kind
        req.Arch = arch
        req.ClusterType = cluster_type
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.GetTkeAppChartList(req)
        return response

    @retry_with_conditions(3, 10)
    def get_upgrade_instance_progress(self, cluster_id=None, limit=None, offset=None, **kwargs):
        """获得节点升级当前的进度，若集群未处于节点升级状态，则接口会报错：任务未找到。
        :param cluster_id: 集群ID
        :type cluster_id: str
        :param limit: 最多获取多少个节点的进度
        :type limit: int
        :param offset: 从第几个节点开始获取进度
        :type offset: int
        
        """
        req = self.model_v20180525.GetUpgradeInstanceProgressRequest()
        req.ClusterId = cluster_id
        req.Limit = limit
        req.Offset = offset
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.GetUpgradeInstanceProgress(req)
        return response

    @retry_with_conditions(3, 10)
    def install_addon(self, cluster_id=None, addon_name=None, addon_version=None, raw_values=None, dry_run=None, **kwargs):
        """为目标集群安装一个addon
        :param cluster_id: 集群ID（仅支持标准tke集群）
        :type cluster_id: str
        :param addon_name: addon名称
        :type addon_name: str
        :param addon_version: addon版本（不传默认安装最新版本）
        :type addon_version: str
        :param raw_values: addon的参数，是一个json格式的base64转码后的字符串（addon参数由DescribeAddonValues获取）
        :type raw_values: str
        :param dry_run: 是否仅做安装检查，设置为true时仅做检查，不会安装组件
        :type dry_run: bool
        
        """
        req = self.model_v20180525.InstallAddonRequest()
        req.ClusterId = cluster_id
        req.AddonName = addon_name
        req.AddonVersion = addon_version
        req.RawValues = raw_values
        req.DryRun = dry_run
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.InstallAddon(req)
        return response

    @retry_with_conditions(3, 10)
    def install_edge_log_agent(self, cluster_id=None, **kwargs):
        """在tke@edge集群的边缘节点上安装日志采集组件
        :param cluster_id: 集群ID
        :type cluster_id: str
        
        """
        req = self.model_v20180525.InstallEdgeLogAgentRequest()
        req.ClusterId = cluster_id
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.InstallEdgeLogAgent(req)
        return response

    @retry_with_conditions(3, 10)
    def install_log_agent(self, cluster_id=None, kubelet_root_dir=None, cluster_type=None, **kwargs):
        """在TKE集群中安装CLS日志采集组件
        :param cluster_id: TKE集群ID
        :type cluster_id: str
        :param kubelet_root_dir: kubelet根目录
        :type kubelet_root_dir: str
        :param cluster_type: 集群类型 tke/eks，默认tke
        :type cluster_type: str
        
        """
        req = self.model_v20180525.InstallLogAgentRequest()
        req.ClusterId = cluster_id
        req.KubeletRootDir = kubelet_root_dir
        req.ClusterType = cluster_type
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.InstallLogAgent(req)
        return response

    @retry_with_conditions(3, 10)
    def list_cluster_inspection_results(self, cluster_ids=None, hide=None, name=None, **kwargs):
        """查询指定集群的巡检结果信息
        :param cluster_ids: 目标集群列表，为空查询用户所有集群

        :type cluster_ids: list of str
        :param hide: 隐藏的字段信息，为了减少无效的字段返回，隐藏字段不会在返回值中返回。可选值：results

        :type hide: list of str
        :param name: 指定查询结果的报告名称，默认查询最新的每个集群只查询最新的一条
        :type name: str
        
        """
        req = self.model_v20180525.ListClusterInspectionResultsRequest()
        req.ClusterIds = cluster_ids
        req.Hide = hide
        req.Name = name
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.ListClusterInspectionResults(req)
        return response

    @retry_with_conditions(3, 10)
    def list_cluster_inspection_results_items(self, cluster_id=None, start_time=None, end_time=None, **kwargs):
        """查询集群巡检结果历史列表
        :param cluster_id: 目标集群ID
        :type cluster_id: str
        :param start_time: 查询历史结果的开始时间，Unix时间戳
        :type start_time: str
        :param end_time: 查询历史结果的结束时间，默认当前距离开始时间3天，Unix时间戳
        :type end_time: str
        
        """
        req = self.model_v20180525.ListClusterInspectionResultsItemsRequest()
        req.ClusterId = cluster_id
        req.StartTime = start_time
        req.EndTime = end_time
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.ListClusterInspectionResultsItems(req)
        return response

    @retry_with_conditions(3, 10)
    def modify_cluster_as_group_attribute(self, cluster_id=None, cluster_as_group_attribute=None, **kwargs):
        """修改集群伸缩组属性
        :param cluster_id: 集群ID
        :type cluster_id: str
        :param cluster_as_group_attribute: 集群关联的伸缩组属性
        :type cluster_as_group_attribute: :class:`tencentcloud.tke.v20180525.models.cluster_as_group_attribute`
        
        """
        req = self.model_v20180525.ModifyClusterAsGroupAttributeRequest()
        req.ClusterId = cluster_id
        req.ClusterAsGroupAttribute = cluster_as_group_attribute
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.ModifyClusterAsGroupAttribute(req)
        return response

    @retry_with_conditions(3, 10)
    def modify_cluster_as_group_option_attribute(self, cluster_id=None, cluster_as_group_option=None, **kwargs):
        """修改集群弹性伸缩属性
        :param cluster_id: 集群ID
        :type cluster_id: str
        :param cluster_as_group_option: 集群弹性伸缩属性
        :type cluster_as_group_option: :class:`tencentcloud.tke.v20180525.models.cluster_as_group_option`
        
        """
        req = self.model_v20180525.ModifyClusterAsGroupOptionAttributeRequest()
        req.ClusterId = cluster_id
        req.ClusterAsGroupOption = cluster_as_group_option
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.ModifyClusterAsGroupOptionAttribute(req)
        return response

    @retry_with_conditions(3, 10)
    def modify_cluster_attribute(self, cluster_id=None, project_id=None, cluster_name=None, cluster_desc=None, cluster_level=None, auto_upgrade_cluster_level=None, qgpu_share_enable=None, cluster_property=None, **kwargs):
        """修改集群属性
        :param cluster_id: 集群ID
        :type cluster_id: str
        :param project_id: 集群所属项目
        :type project_id: int
        :param cluster_name: 集群名称
        :type cluster_name: str
        :param cluster_desc: 集群描述
        :type cluster_desc: str
        :param cluster_level: 集群等级
        :type cluster_level: str
        :param _AutoUpgradecluster_level: 自动变配集群等级
        :type AutoUpgradecluster_level: :class:`tencentcloud.tke.v20180525.models.AutoUpgradecluster_level`
        :param qgpu_share_enable: 是否开启QGPU共享
        :type qgpu_share_enable: bool
        :param cluster_property: 集群属性
        :type cluster_property: :class:`tencentcloud.tke.v20180525.models.cluster_property`
        
        """
        req = self.model_v20180525.ModifyClusterAttributeRequest()
        req.ClusterId = cluster_id
        req.ProjectId = project_id
        req.ClusterName = cluster_name
        req.ClusterDesc = cluster_desc
        req.ClusterLevel = cluster_level
        req.AutoUpgradeClusterLevel = auto_upgrade_cluster_level
        req.QGPUShareEnable = qgpu_share_enable
        req.ClusterProperty = cluster_property
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.ModifyClusterAttribute(req)
        return response

    @retry_with_conditions(3, 10)
    def modify_cluster_authentication_options(self, cluster_id=None, service_accounts=None, oidc_config=None, **kwargs):
        """修改集群认证配置
        :param cluster_id: 集群ID
        :type cluster_id: str
        :param service_accounts: ServiceAccount认证配置
        :type service_accounts: :class:`tencentcloud.tke.v20180525.models.ServiceAccountAuthenticationOptions`
        :param oidc_config: OIDC认证配置
        :type oidc_config: :class:`tencentcloud.tke.v20180525.models.oidc_configAuthenticationOptions`
        
        """
        req = self.model_v20180525.ModifyClusterAuthenticationOptionsRequest()
        req.ClusterId = cluster_id
        req.ServiceAccounts = service_accounts
        req.OIDCConfig = oidc_config
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.ModifyClusterAuthenticationOptions(req)
        return response

    @retry_with_conditions(3, 10)
    def modify_cluster_endpoint_sp(self, cluster_id=None, security_policies=None, security_group=None, **kwargs):
        """修改托管集群外网端口的安全策略（老的方式，仅支持托管集群外网端口）
        :param cluster_id: 集群ID
        :type cluster_id: str
        :param security_policies: 安全策略放通单个IP或CIDR(例如: "192.168.1.0/24",默认为拒绝所有)
        :type security_policies: list of str
        :param security_group: 修改外网访问安全组
        :type security_group: str
        
        """
        req = self.model_v20180525.ModifyClusterEndpointSPRequest()
        req.ClusterId = cluster_id
        req.SecurityPolicies = security_policies
        req.SecurityGroup = security_group
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.ModifyClusterEndpointSP(req)
        return response

    @retry_with_conditions(3, 10)
    def modify_cluster_image(self, cluster_id=None, image_id=None, **kwargs):
        """修改集群镜像
        :param cluster_id: 集群ID
        :type cluster_id: str
        :param image_id: 指定有效的镜像ID，格式形如img-e55paxnt。可通过登录控制台查询，也可调用接口 [DescribeImages](https://cloud.tencent.com/document/api/213/15715)，取返回信息中的image_id字段。
        :type image_id: str
        
        """
        req = self.model_v20180525.ModifyClusterImageRequest()
        req.ClusterId = cluster_id
        req.ImageId = image_id
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.ModifyClusterImage(req)
        return response

    @retry_with_conditions(3, 10)
    def modify_cluster_node_pool(self, cluster_id=None, node_pool_id=None, name=None, max_nodes_num=None, min_nodes_num=None, labels=None, taints=None, annotations=None, enable_autoscale=None, os_name=None, os_customize_type=None, gpu_args=None, user_script=None, ignore_existed_node=None, extra_args=None, tags=None, unschedulable=None, deletion_protection=None, docker_graph_path=None, pre_start_user_script=None, **kwargs):
        """编辑节点池
        :param cluster_id: 集群ID
        :type cluster_id: str
        :param node_pool_id: 节点池ID
        :type node_pool_id: str
        :param name: 名称
        :type name: str
        :param max_nodes_num: 最大节点数
        :type max_nodes_num: int
        :param min_nodes_num: 最小节点数
        :type min_nodes_num: int
        :param labels: 标签
        :type labels: list of Label
        :param taints: 污点
        :type taints: list of Taint
        :param annotations: 节点 Annotation 列表
        :type annotations: list of AnnotationValue
        :param enable_autoscale: 是否开启伸缩
        :type enable_autoscale: bool
        :param _Osname: 操作系统名称
        :type Osname: str
        :param os_customize_type: 镜像版本，"DOCKER_CUSTOMIZE"(容器定制版),"GENERAL"(普通版本，默认值)
        :type os_customize_type: str
        :param gpu_args: GPU驱动版本，CUDA版本，cuDNN版本以及是否启用MIG特性
        :type gpu_args: :class:`tencentcloud.tke.v20180525.models.gpu_args`
        :param user_script: base64编码后的自定义脚本
        :type user_script: str
        :param ignore_existed_node: 更新label和taint时忽略存量节点
        :type ignore_existed_node: bool
        :param extra_args: 节点自定义参数
        :type extra_args: :class:`tencentcloud.tke.v20180525.models.Instanceextra_args`
        :param tags: 资源标签
        :type tags: list of Tag
        :param unschedulable: 设置加入的节点是否参与调度，默认值为0，表示参与调度；非0表示不参与调度, 待节点初始化完成之后, 可执行kubectl uncordon nodename使node加入调度.
        :type unschedulable: int
        :param deletion_protection: 删除保护开关
        :type deletion_protection: bool
        :param docker_graph_path: dockerd --graph 指定值, 默认为 /var/lib/docker
        :type docker_graph_path: str
        :param _PreStartuser_script: base64编码后的自定义脚本
        :type PreStartuser_script: str
        
        """
        req = self.model_v20180525.ModifyClusterNodePoolRequest()
        req.ClusterId = cluster_id
        req.NodePoolId = node_pool_id
        req.Name = name
        req.MaxNodesNum = max_nodes_num
        req.MinNodesNum = min_nodes_num
        req.Labels = labels
        req.Taints = taints
        req.Annotations = annotations
        req.EnableAutoscale = enable_autoscale
        req.OsName = os_name
        req.OsCustomizeType = os_customize_type
        req.GPUArgs = gpu_args
        req.UserScript = user_script
        req.IgnoreExistedNode = ignore_existed_node
        req.ExtraArgs = extra_args
        req.Tags = tags
        req.Unschedulable = unschedulable
        req.DeletionProtection = deletion_protection
        req.DockerGraphPath = docker_graph_path
        req.PreStartUserScript = pre_start_user_script
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.ModifyClusterNodePool(req)
        return response

    @retry_with_conditions(3, 10)
    def modify_cluster_runtime_config(self, cluster_id=None, dst_k8_s_version=None, cluster_runtime_config=None, node_pool_runtime_config=None, **kwargs):
        """修改集群及节点池纬度运行时配置
        :param cluster_id: 集群ID，必填
        :type cluster_id: str
        :param dst_k8_s_version: 当需要修改运行时版本是根据另外的K8S版本获取时，需填写。例如升级校验有冲突后修改场景
        :type dst_k8_s_version: str
        :param cluster_runtime_config: 需要修改集群运行时时填写
        :type cluster_runtime_config: :class:`tencentcloud.tke.v20180525.models.RuntimeConfig`
        :param node_pool_runtime_config: 需要修改节点池运行时时，填需要修改的部分
        :type node_pool_runtime_config: list of NodePoolRuntime
        
        """
        req = self.model_v20180525.ModifyClusterRuntimeConfigRequest()
        req.ClusterId = cluster_id
        req.DstK8SVersion = dst_k8_s_version
        req.ClusterRuntimeConfig = cluster_runtime_config
        req.NodePoolRuntimeConfig = node_pool_runtime_config
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.ModifyClusterRuntimeConfig(req)
        return response

    @retry_with_conditions(3, 10)
    def modify_cluster_tags(self, cluster_id=None, tags=None, sync_subresource=None, **kwargs):
        """修改集群标签
        :param cluster_id: 集群ID
        :type cluster_id: str
        :param tags: 集群标签
        :type tags: list of Tag
        :param sync_subresource: 是否同步集群内子资源标签
        :type sync_subresource: bool
        
        """
        req = self.model_v20180525.ModifyClusterTagsRequest()
        req.ClusterId = cluster_id
        req.Tags = tags
        req.SyncSubresource = sync_subresource
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.ModifyClusterTags(req)
        return response

    @retry_with_conditions(3, 10)
    def modify_cluster_virtual_node_pool(self, cluster_id=None, node_pool_id=None, name=None, security_group_ids=None, labels=None, taints=None, deletion_protection=None, **kwargs):
        """修改超级节点池
        :param cluster_id: 集群ID
        :type cluster_id: str
        :param node_pool_id: 节点池ID
        :type node_pool_id: str
        :param name: 节点池名称
        :type name: str
        :param security_group_ids: 安全组ID列表
        :type security_group_ids: list of str
        :param labels: 虚拟节点label
        :type labels: list of Label
        :param taints: 虚拟节点taint
        :type taints: list of Taint
        :param deletion_protection: 删除保护开关
        :type deletion_protection: bool
        
        """
        req = self.model_v20180525.ModifyClusterVirtualNodePoolRequest()
        req.ClusterId = cluster_id
        req.NodePoolId = node_pool_id
        req.Name = name
        req.SecurityGroupIds = security_group_ids
        req.Labels = labels
        req.Taints = taints
        req.DeletionProtection = deletion_protection
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.ModifyClusterVirtualNodePool(req)
        return response

    @retry_with_conditions(3, 10)
    def modify_node_pool_desired_capacity_about_asg(self, cluster_id=None, node_pool_id=None, desired_capacity=None, **kwargs):
        """修改节点池关联伸缩组的期望实例数
        :param cluster_id: 集群id
        :type cluster_id: str
        :param node_pool_id: 节点池id
        :type node_pool_id: str
        :param desired_capacity: 节点池所关联的伸缩组的期望实例数
        :type desired_capacity: int
        
        """
        req = self.model_v20180525.ModifyNodePoolDesiredCapacityAboutAsgRequest()
        req.ClusterId = cluster_id
        req.NodePoolId = node_pool_id
        req.DesiredCapacity = desired_capacity
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.ModifyNodePoolDesiredCapacityAboutAsg(req)
        return response

    @retry_with_conditions(3, 10)
    def modify_node_pool_instance_types(self, cluster_id=None, node_pool_id=None, instance_types=None, **kwargs):
        """修改节点池的机型配置
        :param cluster_id: 集群id
        :type cluster_id: str
        :param node_pool_id: 节点池id
        :type node_pool_id: str
        :param instance_types: 机型列表，主实例机型不支持修改
        :type instance_types: list of str
        
        """
        req = self.model_v20180525.ModifyNodePoolInstanceTypesRequest()
        req.ClusterId = cluster_id
        req.NodePoolId = node_pool_id
        req.InstanceTypes = instance_types
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.ModifyNodePoolInstanceTypes(req)
        return response

    @retry_with_conditions(3, 10)
    def modify_open_policy_list(self, cluster_id=None, open_policy_info_list=None, category=None, **kwargs):
        """批量修改opa策略
        :param cluster_id: 集群ID
        :type cluster_id: str
        :param open_policy_info_list: 修改的策略列表，目前仅支持修改EnforcementAction字段
        :type open_policy_info_list: list of OpenPolicySwitch
        :param category: 策略分类 基线：baseline 优选：priority 可选：optional
        :type category: str
        
        """
        req = self.model_v20180525.ModifyOpenPolicyListRequest()
        req.ClusterId = cluster_id
        req.OpenPolicyInfoList = open_policy_info_list
        req.Category = category
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.ModifyOpenPolicyList(req)
        return response

    @retry_with_conditions(3, 10)
    def modify_prometheus_agent_external_labels(self, instance_id=None, cluster_id=None, external_labels=None, **kwargs):
        """修改被关联集群的external labels
        :param instance_id: 实例ID
        :type instance_id: str
        :param cluster_id: 集群ID
        :type cluster_id: str
        :param external_labels: 新的external_labels
        :type external_labels: list of Label
        
        """
        req = self.model_v20180525.ModifyPrometheusAgentExternalLabelsRequest()
        req.InstanceId = instance_id
        req.ClusterId = cluster_id
        req.ExternalLabels = external_labels
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.ModifyPrometheusAgentExternalLabels(req)
        return response

    @retry_with_conditions(3, 10)
    def modify_prometheus_alert_policy(self, instance_id=None, alert_rule=None, **kwargs):
        """修改2.0实例告警策略
        :param instance_id: 实例id
        :type instance_id: str
        :param alert_rule: 告警配置
        :type alert_rule: :class:`tencentcloud.tke.v20180525.models.PrometheusAlertPolicyItem`
        
        """
        req = self.model_v20180525.ModifyPrometheusAlertPolicyRequest()
        req.InstanceId = instance_id
        req.AlertRule = alert_rule
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.ModifyPrometheusAlertPolicy(req)
        return response

    @retry_with_conditions(3, 10)
    def modify_prometheus_alert_rule(self, instance_id=None, alert_rule=None, **kwargs):
        """修改告警规则
        :param instance_id: 实例id
        :type instance_id: str
        :param alert_rule: 告警配置
        :type alert_rule: :class:`tencentcloud.tke.v20180525.models.Prometheusalert_ruleDetail`
        
        """
        req = self.model_v20180525.ModifyPrometheusAlertRuleRequest()
        req.InstanceId = instance_id
        req.AlertRule = alert_rule
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.ModifyPrometheusAlertRule(req)
        return response

    @retry_with_conditions(3, 10)
    def modify_prometheus_config(self, instance_id=None, cluster_type=None, cluster_id=None, service_monitors=None, pod_monitors=None, raw_jobs=None, probes=None, **kwargs):
        """修改集群采集配置
        :param instance_id: 实例id
        :type instance_id: str
        :param cluster_type: 集群类型
        :type cluster_type: str
        :param cluster_id: 集群id
        :type cluster_id: str
        :param service_monitors: service_monitors配置
        :type service_monitors: list of PrometheusConfigItem
        :param pod_monitors: pod_monitors配置
        :type pod_monitors: list of PrometheusConfigItem
        :param raw_jobs: prometheus原生Job配置
        :type raw_jobs: list of PrometheusConfigItem
        :param probes: probes 配置
        :type probes: list of PrometheusConfigItem
        
        """
        req = self.model_v20180525.ModifyPrometheusConfigRequest()
        req.InstanceId = instance_id
        req.ClusterType = cluster_type
        req.ClusterId = cluster_id
        req.ServiceMonitors = service_monitors
        req.PodMonitors = pod_monitors
        req.RawJobs = raw_jobs
        req.Probes = probes
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.ModifyPrometheusConfig(req)
        return response

    @retry_with_conditions(3, 10)
    def modify_prometheus_global_notification(self, instance_id=None, notification=None, **kwargs):
        """修改全局告警通知渠道
        :param instance_id: 实例ID
        :type instance_id: str
        :param notification: 告警通知渠道
        :type notification: :class:`tencentcloud.tke.v20180525.models.PrometheusnotificationItem`
        
        """
        req = self.model_v20180525.ModifyPrometheusGlobalNotificationRequest()
        req.InstanceId = instance_id
        req.Notification = notification
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.ModifyPrometheusGlobalNotification(req)
        return response

    @retry_with_conditions(3, 10)
    def modify_prometheus_record_rule_yaml(self, instance_id=None, name=None, content=None, **kwargs):
        """修改聚合规则yaml方式
        :param instance_id: 实例id
        :type instance_id: str
        :param name: 聚合实例名称
        :type name: str
        :param content: 新的内容
        :type content: str
        
        """
        req = self.model_v20180525.ModifyPrometheusRecordRuleYamlRequest()
        req.InstanceId = instance_id
        req.Name = name
        req.Content = content
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.ModifyPrometheusRecordRuleYaml(req)
        return response

    @retry_with_conditions(3, 10)
    def modify_prometheus_temp(self, template_id=None, template=None, **kwargs):
        """修改模板内容
        :param template_id: 模板ID
        :type template_id: str
        :param template: 修改内容
        :type template: :class:`tencentcloud.tke.v20180525.models.PrometheusTempModify`
        
        """
        req = self.model_v20180525.ModifyPrometheusTempRequest()
        req.TemplateId = template_id
        req.Template = template
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.ModifyPrometheusTemp(req)
        return response

    @retry_with_conditions(3, 10)
    def modify_prometheus_template(self, template_id=None, template=None, **kwargs):
        """修改模板内容
        :param template_id: 模板ID
        :type template_id: str
        :param template: 修改内容
        :type template: :class:`tencentcloud.tke.v20180525.models.PrometheustemplateModify`
        
        """
        req = self.model_v20180525.ModifyPrometheusTemplateRequest()
        req.TemplateId = template_id
        req.Template = template
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.ModifyPrometheusTemplate(req)
        return response

    @retry_with_conditions(3, 10)
    def modify_reserved_instance_scope(self, reserved_instance_ids=None, reserved_instance_scope=None, **kwargs):
        """修改预留券的抵扣范围，抵扣范围取值：Region、Zone 和 Node。
        :param reserved_instance_ids: 预留券唯一 ID
        :type reserved_instance_ids: list of str
        :param reserved_instance_scope: 预留券抵扣范围信息
        :type reserved_instance_scope: :class:`tencentcloud.tke.v20180525.models.reserved_instance_scope`
        
        """
        req = self.model_v20180525.ModifyReservedInstanceScopeRequest()
        req.ReservedInstanceIds = reserved_instance_ids
        req.ReservedInstanceScope = reserved_instance_scope
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.ModifyReservedInstanceScope(req)
        return response

    @retry_with_conditions(3, 10)
    def remove_node_from_node_pool(self, cluster_id=None, node_pool_id=None, instance_ids=None, **kwargs):
        """移出节点池节点，但保留在集群内
        :param cluster_id: 集群id
        :type cluster_id: str
        :param node_pool_id: 节点池id
        :type node_pool_id: str
        :param instance_ids: 节点id列表，一次最多支持100台
        :type instance_ids: list of str
        
        """
        req = self.model_v20180525.RemoveNodeFromNodePoolRequest()
        req.ClusterId = cluster_id
        req.NodePoolId = node_pool_id
        req.InstanceIds = instance_ids
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.RemoveNodeFromNodePool(req)
        return response

    @retry_with_conditions(3, 10)
    def renew_reserved_instances(self, reserved_instance_ids=None, instance_charge_prepaid=None, client_token=None, **kwargs):
        """续费时请确保账户余额充足。
        :param reserved_instance_ids: 预留券实例ID，每次请求实例的上限为100。
        :type reserved_instance_ids: list of str
        :param instance_charge_prepaid: 预付费模式，即包年包月相关参数设置。通过该参数可以指定包年包月实例的续费时长、是否设置自动续费等属性。
        :type instance_charge_prepaid: :class:`tencentcloud.tke.v20180525.models.instance_charge_prepaid`
        :param client_token: 用于保证请求幂等性的字符串。该字符串由客户生成，需保证不同请求之间唯一，最大值不超过64个ASCII字符。若不指定该参数，则无法保证请求的幂等性。
        :type client_token: str
        
        """
        req = self.model_v20180525.RenewReservedInstancesRequest()
        req.ReservedInstanceIds = reserved_instance_ids
        req.InstanceChargePrepaid = instance_charge_prepaid
        req.ClientToken = client_token
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.RenewReservedInstances(req)
        return response

    @retry_with_conditions(3, 10)
    def restart_eks_container_instances(self, eks_ci_ids=None, **kwargs):
        """重启弹性容器实例，支持批量操作
        :param eks_ci_ids: EKS instance ids
        :type eks_ci_ids: list of str
        
        """
        req = self.model_v20180525.RestartEKSContainerInstancesRequest()
        req.EksCiIds = eks_ci_ids
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.RestartEKSContainerInstances(req)
        return response

    @retry_with_conditions(3, 10)
    def rollback_cluster_release(self, cluster_id=None, name=None, namespace=None, revision=None, cluster_type=None, **kwargs):
        """在应用市场中集群回滚应用至某个历史版本
        :param cluster_id: 集群ID
        :type cluster_id: str
        :param name: 应用名称
        :type name: str
        :param namespace: 应用命名空间
        :type namespace: str
        :param revision: 回滚版本号
        :type revision: int
        :param cluster_type: 集群类型
        :type cluster_type: str
        
        """
        req = self.model_v20180525.RollbackClusterReleaseRequest()
        req.ClusterId = cluster_id
        req.Name = name
        req.Namespace = namespace
        req.Revision = revision
        req.ClusterType = cluster_type
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.RollbackClusterRelease(req)
        return response

    @retry_with_conditions(3, 10)
    def run_prometheus_instance(self, instance_id=None, subnet_id=None, **kwargs):
        """初始化TMP实例，开启集成中心时调用
        :param instance_id: 实例ID
        :type instance_id: str
        :param subnet_id: 子网ID，默认使用实例所用子网初始化，也可通过该参数传递新的子网ID初始化
        :type subnet_id: str
        
        """
        req = self.model_v20180525.RunPrometheusInstanceRequest()
        req.InstanceId = instance_id
        req.SubnetId = subnet_id
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.RunPrometheusInstance(req)
        return response

    @retry_with_conditions(3, 10)
    def scale_in_cluster_master(self, cluster_id=None, scale_in_masters=None, **kwargs):
        """缩容独立集群master节点，本功能为内测能力，使用之前请先提单联系我们。
        :param cluster_id: 集群实例ID
        :type cluster_id: str
        :param scale_in_masters: master缩容选项
        :type scale_in_masters: list of ScaleInMaster
        
        """
        req = self.model_v20180525.ScaleInClusterMasterRequest()
        req.ClusterId = cluster_id
        req.ScaleInMasters = scale_in_masters
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.ScaleInClusterMaster(req)
        return response

    @retry_with_conditions(3, 10)
    def scale_out_cluster_master(self, cluster_id=None, run_instances_for_node=None, existed_instances_for_node=None, instance_advanced_settings=None, extra_args=None, **kwargs):
        """扩容独立集群master节点
        :param cluster_id: 集群实例ID
        :type cluster_id: str
        :param run_instances_for_node: 新建节点参数
        :type run_instances_for_node: list of run_instances_for_node
        :param existed_instances_for_node: 添加已有节点相关参数
        :type existed_instances_for_node: list of existed_instances_for_node
        :param instance_advanced_settings: 实例高级设置
        :type instance_advanced_settings: :class:`tencentcloud.tke.v20180525.models.instance_advanced_settings`
        :param extra_args: 集群master组件自定义参数
        :type extra_args: :class:`tencentcloud.tke.v20180525.models.Clusterextra_args`
        
        """
        req = self.model_v20180525.ScaleOutClusterMasterRequest()
        req.ClusterId = cluster_id
        req.RunInstancesForNode = run_instances_for_node
        req.ExistedInstancesForNode = existed_instances_for_node
        req.InstanceAdvancedSettings = instance_advanced_settings
        req.ExtraArgs = extra_args
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.ScaleOutClusterMaster(req)
        return response

    @retry_with_conditions(3, 10)
    def set_node_pool_node_protection(self, cluster_id=None, node_pool_id=None, instance_ids=None, protected_from_scale_in=None, **kwargs):
        """仅能设置节点池中处于伸缩组的节点
        :param cluster_id: 集群id
        :type cluster_id: str
        :param node_pool_id: 节点池id
        :type node_pool_id: str
        :param instance_ids: 节点id
        :type instance_ids: list of str
        :param protected_from_scale_in: 节点是否需要移出保护
        :type protected_from_scale_in: bool
        
        """
        req = self.model_v20180525.SetNodePoolNodeProtectionRequest()
        req.ClusterId = cluster_id
        req.NodePoolId = node_pool_id
        req.InstanceIds = instance_ids
        req.ProtectedFromScaleIn = protected_from_scale_in
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.SetNodePoolNodeProtection(req)
        return response

    @retry_with_conditions(3, 10)
    def sync_prometheus_temp(self, template_id=None, targets=None, **kwargs):
        """同步模板到实例或者集群，针对V2版本实例
        :param template_id: 实例id
        :type template_id: str
        :param targets: 同步目标
        :type targets: list of PrometheusTemplateSyncTarget
        
        """
        req = self.model_v20180525.SyncPrometheusTempRequest()
        req.TemplateId = template_id
        req.Targets = targets
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.SyncPrometheusTemp(req)
        return response

    @retry_with_conditions(3, 10)
    def sync_prometheus_template(self, template_id=None, targets=None, **kwargs):
        """同步模板到实例或者集群
        :param template_id: 实例id
        :type template_id: str
        :param targets: 同步目标
        :type targets: list of PrometheusTemplateSyncTarget
        
        """
        req = self.model_v20180525.SyncPrometheusTemplateRequest()
        req.TemplateId = template_id
        req.Targets = targets
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.SyncPrometheusTemplate(req)
        return response

    @retry_with_conditions(3, 10)
    def uninstall_cluster_release(self, cluster_id=None, name=None, namespace=None, cluster_type=None, **kwargs):
        """在应用市场中集群删除某个应用
        :param cluster_id: 集群ID
        :type cluster_id: str
        :param name: 应用名称
        :type name: str
        :param namespace: 应用命名空间
        :type namespace: str
        :param cluster_type: 集群类型
        :type cluster_type: str
        
        """
        req = self.model_v20180525.UninstallClusterReleaseRequest()
        req.ClusterId = cluster_id
        req.Name = name
        req.Namespace = namespace
        req.ClusterType = cluster_type
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.UninstallClusterRelease(req)
        return response

    @retry_with_conditions(3, 10)
    def uninstall_edge_log_agent(self, cluster_id=None, **kwargs):
        """从tke@edge集群边缘节点上卸载日志采集组件
        :param cluster_id: 集群ID
        :type cluster_id: str
        
        """
        req = self.model_v20180525.UninstallEdgeLogAgentRequest()
        req.ClusterId = cluster_id
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.UninstallEdgeLogAgent(req)
        return response

    @retry_with_conditions(3, 10)
    def uninstall_log_agent(self, cluster_id=None, **kwargs):
        """从TKE集群中卸载CLS日志采集组件
        :param cluster_id: 集群ID
        :type cluster_id: str
        
        """
        req = self.model_v20180525.UninstallLogAgentRequest()
        req.ClusterId = cluster_id
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.UninstallLogAgent(req)
        return response

    @retry_with_conditions(3, 10)
    def update_addon(self, cluster_id=None, addon_name=None, addon_version=None, raw_values=None, update_strategy=None, dry_run=None, **kwargs):
        """更新一个addon的参数和版本
        :param cluster_id: 集群ID
        :type cluster_id: str
        :param addon_name: addon名称
        :type addon_name: str
        :param addon_version: addon版本（不传默认不更新，不传addon_version时raw_values必传）
        :type addon_version: str
        :param raw_values: addon的参数，是一个json格式的base64转码后的字符串（addon参数由DescribeAddonValues获取，不传raw_values时addon_version必传））
        :type raw_values: str
        :param update_strategy: addon参数的更新策略，支持replace和merge两种策略，默认值为merge，兼容旧版本API。replace：使用新raw_values全量替换addon原raw_values，merge：根据新raw_values新增或更新addon原raw_values中对应参数。
        :type update_strategy: str
        :param dry_run: 是否仅做更新检查，设置为true时仅做检查，不会更新组件
        :type dry_run: bool
        
        """
        req = self.model_v20180525.UpdateAddonRequest()
        req.ClusterId = cluster_id
        req.AddonName = addon_name
        req.AddonVersion = addon_version
        req.RawValues = raw_values
        req.UpdateStrategy = update_strategy
        req.DryRun = dry_run
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.UpdateAddon(req)
        return response

    @retry_with_conditions(3, 10)
    def update_cluster_kubeconfig(self, cluster_id=None, sub_accounts=None, **kwargs):
        """对集群的Kubeconfig信息进行更新
        :param cluster_id: 集群ID
        :type cluster_id: str
        :param sub_accounts: 子账户Uin列表，传空默认为调用此接口的SubUin
        :type sub_accounts: list of str
        
        """
        req = self.model_v20180525.UpdateClusterKubeconfigRequest()
        req.ClusterId = cluster_id
        req.SubAccounts = sub_accounts
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.UpdateClusterKubeconfig(req)
        return response

    @retry_with_conditions(3, 10)
    def update_cluster_version(self, cluster_id=None, dst_version=None, extra_args=None, max_not_ready_percent=None, skip_pre_check=None, **kwargs):
        """升级集群 Master 组件到指定版本
        :param cluster_id: 集群 Id
        :type cluster_id: str
        :param dst_version: 需要升级到的版本
        :type dst_version: str
        :param extra_args: 集群自定义参数
        :type extra_args: :class:`tencentcloud.tke.v20180525.models.Clusterextra_args`
        :param max_not_ready_percent: 可容忍的最大不可用pod数目
        :type max_not_ready_percent: float
        :param skip_pre_check: 是否跳过预检查阶段
        :type skip_pre_check: bool
        
        """
        req = self.model_v20180525.UpdateClusterVersionRequest()
        req.ClusterId = cluster_id
        req.DstVersion = dst_version
        req.ExtraArgs = extra_args
        req.MaxNotReadyPercent = max_not_ready_percent
        req.SkipPreCheck = skip_pre_check
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.UpdateClusterVersion(req)
        return response

    @retry_with_conditions(3, 10)
    def update_eks_cluster(self, cluster_id=None, cluster_name=None, cluster_desc=None, subnet_ids=None, public_lb=None, internal_lb=None, service_subnet_id=None, dns_servers=None, clear_dns_server=None, need_delete_cbs=None, proxy_lb=None, extra_param=None, **kwargs):
        """修改弹性集群名称等属性
        :param cluster_id: 弹性集群Id
        :type cluster_id: str
        :param cluster_name: 弹性集群名称
        :type cluster_name: str
        :param cluster_desc: 弹性集群描述信息
        :type cluster_desc: str
        :param subnet_ids: 子网Id 列表
        :type subnet_ids: list of str
        :param public_lb: 弹性容器集群公网访问LB信息
        :type public_lb: :class:`tencentcloud.tke.v20180525.models.Clusterpublic_lb`
        :param internal_lb: 弹性容器集群内网访问LB信息
        :type internal_lb: :class:`tencentcloud.tke.v20180525.models.Clusterinternal_lb`
        :param service_subnet_id: Service 子网Id
        :type service_subnet_id: str
        :param dns_servers: 集群自定义的dns 服务器信息
        :type dns_servers: list of DnsServerConf
        :param clear_dns_server: 是否清空自定义dns 服务器设置。为1 表示 是。其他表示 否。
        :type clear_dns_server: str
        :param need_delete_cbs: 将来删除集群时是否要删除cbs。默认为 FALSE
        :type need_delete_cbs: bool
        :param proxy_lb: 标记是否是新的内外网。默认为false
        :type proxy_lb: bool
        :param extra_param: 扩展参数。须是map[string]string 的json 格式。
        :type extra_param: str
        
        """
        req = self.model_v20180525.UpdateEKSClusterRequest()
        req.ClusterId = cluster_id
        req.ClusterName = cluster_name
        req.ClusterDesc = cluster_desc
        req.SubnetIds = subnet_ids
        req.PublicLB = public_lb
        req.InternalLB = internal_lb
        req.ServiceSubnetId = service_subnet_id
        req.DnsServers = dns_servers
        req.ClearDnsServer = clear_dns_server
        req.NeedDeleteCbs = need_delete_cbs
        req.ProxyLB = proxy_lb
        req.ExtraParam = extra_param
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.UpdateEKSCluster(req)
        return response

    @retry_with_conditions(3, 10)
    def update_eks_container_instance(self, eks_ci_id=None, restart_policy=None, eks_ci_volume=None, containers=None, init_containers=None, name=None, image_registry_credentials=None, **kwargs):
        """更新容器实例
        :param eks_ci_id: 容器实例 ID
        :type eks_ci_id: str
        :param restart_policy: 实例重启策略： Always(总是重启)、Never(从不重启)、OnFailure(失败时重启)
        :type restart_policy: str
        :param eks_ci_volume: 数据卷，包含NfsVolume数组和CbsVolume数组
        :type eks_ci_volume: :class:`tencentcloud.tke.v20180525.models.eks_ci_volume`
        :param containers: 容器组
        :type containers: list of Container
        :param _Initcontainers: Init 容器组
        :type Initcontainers: list of Container
        :param name: 容器实例名称
        :type name: str
        :param image_registry_credentials: 镜像仓库凭证数组
        :type image_registry_credentials: list of ImageRegistryCredential
        
        """
        req = self.model_v20180525.UpdateEKSContainerInstanceRequest()
        req.EksCiId = eks_ci_id
        req.RestartPolicy = restart_policy
        req.EksCiVolume = eks_ci_volume
        req.Containers = containers
        req.InitContainers = init_containers
        req.Name = name
        req.ImageRegistryCredentials = image_registry_credentials
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.UpdateEKSContainerInstance(req)
        return response

    @retry_with_conditions(3, 10)
    def update_edge_cluster_version(self, cluster_id=None, edge_version=None, registry_prefix=None, skip_pre_check=None, **kwargs):
        """升级边缘集群组件到指定版本，此版本为TKEEdge专用版本。
        :param cluster_id: 集群 Id
        :type cluster_id: str
        :param edge_version: 需要升级到的版本
        :type edge_version: str
        :param registry_prefix: 自定义边缘组件镜像仓库前缀
        :type registry_prefix: str
        :param skip_pre_check: 是否跳过预检查阶段
        :type skip_pre_check: bool
        
        """
        req = self.model_v20180525.UpdateEdgeClusterVersionRequest()
        req.ClusterId = cluster_id
        req.EdgeVersion = edge_version
        req.RegistryPrefix = registry_prefix
        req.SkipPreCheck = skip_pre_check
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.UpdateEdgeClusterVersion(req)
        return response

    @retry_with_conditions(3, 10)
    def update_image_cache(self, image_cache_id=None, image_cache_name=None, image_registry_credentials=None, images=None, image_cache_size=None, retention_days=None, security_group_ids=None, **kwargs):
        """更新镜像缓存接口
        :param image_cache_id: 镜像缓存ID
        :type image_cache_id: str
        :param image_cache_name: 镜像缓存名称
        :type image_cache_name: str
        :param image_registry_credentials: 镜像仓库凭证数组
        :type image_registry_credentials: list of ImageRegistryCredential
        :param images: 用于制作镜像缓存的容器镜像列表
        :type images: list of str
        :param image_cache_size: 镜像缓存的大小。默认为20 GiB。取值范围参考[云硬盘类型](https://cloud.tencent.com/document/product/362/2353)中的高性能云盘类型的大小限制。
        :type image_cache_size: int
        :param retention_days: 镜像缓存保留时间天数，过期将会自动清理，默认为0，永不过期。
        :type retention_days: int
        :param security_group_ids: 安全组Id
        :type security_group_ids: list of str
        
        """
        req = self.model_v20180525.UpdateImageCacheRequest()
        req.ImageCacheId = image_cache_id
        req.ImageCacheName = image_cache_name
        req.ImageRegistryCredentials = image_registry_credentials
        req.Images = images
        req.ImageCacheSize = image_cache_size
        req.RetentionDays = retention_days
        req.SecurityGroupIds = security_group_ids
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.UpdateImageCache(req)
        return response

    @retry_with_conditions(3, 10)
    def update_tke_edge_cluster(self, cluster_id=None, cluster_name=None, cluster_desc=None, pod_cidr=None, service_cidr=None, public_lb=None, internal_lb=None, core_dns=None, health_region=None, health=None, grid_daemon=None, auto_upgrade_cluster_level=None, cluster_level=None, **kwargs):
        """修改边缘计算集群名称等属性
        :param cluster_id: 边缘计算集群ID
        :type cluster_id: str
        :param cluster_name: 边缘计算集群名称
        :type cluster_name: str
        :param cluster_desc: 边缘计算集群描述信息
        :type cluster_desc: str
        :param pod_cidr: 边缘计算集群的pod cidr
        :type pod_cidr: str
        :param service_cidr: 边缘计算集群的service cidr
        :type service_cidr: str
        :param public_lb: 边缘计算集群公网访问LB信息
        :type public_lb: :class:`tencentcloud.tke.v20180525.models.EdgeClusterpublic_lb`
        :param internal_lb: 边缘计算集群内网访问LB信息
        :type internal_lb: :class:`tencentcloud.tke.v20180525.models.EdgeClusterinternal_lb`
        :param core_dns: 边缘计算集群的core_dns部署信息
        :type core_dns: str
        :param health_region: 边缘计算集群的健康检查多地域部署信息
        :type health_region: str
        :param health: 边缘计算集群的健康检查部署信息
        :type health: str
        :param grid_daemon: 边缘计算集群的grid_daemon部署信息
        :type grid_daemon: str
        :param auto_upgrade_cluster_level: 边缘集群开启自动升配
        :type auto_upgrade_cluster_level: bool
        :param cluster_level: 边缘集群的集群规模
        :type cluster_level: str
        
        """
        req = self.model_v20180525.UpdateTKEEdgeClusterRequest()
        req.ClusterId = cluster_id
        req.ClusterName = cluster_name
        req.ClusterDesc = cluster_desc
        req.PodCIDR = pod_cidr
        req.ServiceCIDR = service_cidr
        req.PublicLB = public_lb
        req.InternalLB = internal_lb
        req.CoreDns = core_dns
        req.HealthRegion = health_region
        req.Health = health
        req.GridDaemon = grid_daemon
        req.AutoUpgradeClusterLevel = auto_upgrade_cluster_level
        req.ClusterLevel = cluster_level
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.UpdateTKEEdgeCluster(req)
        return response

    @retry_with_conditions(3, 10)
    def upgrade_cluster_instances(self, cluster_id=None, operation=None, upgrade_type=None, instance_ids=None, reset_param=None, skip_pre_check=None, max_not_ready_percent=None, upgrade_run_time=None, **kwargs):
        """给集群的一批work节点进行升级
        :param cluster_id: 集群ID
        :type cluster_id: str
        :param operation: create 表示开始一次升级任务
pause 表示停止任务
resume表示继续任务
abort表示终止任务
        :type operation: str
        :param upgrade_type: 升级类型，只有operation是create需要设置
reset 大版本重装升级
hot 小版本热升级
major 大版本原地升级
        :type upgrade_type: str
        :param instance_ids: 需要升级的节点列表
        :type instance_ids: list of str
        :param reset_param: 当节点重新加入集群时候所使用的参数，参考添加已有节点接口
        :type reset_param: :class:`tencentcloud.tke.v20180525.models.UpgradeNodereset_param`
        :param skip_pre_check: 是否忽略节点升级前检查
        :type skip_pre_check: bool
        :param max_not_ready_percent: 最大可容忍的不可用Pod比例
        :type max_not_ready_percent: float
        :param upgrade_run_time: 是否升级节点运行时，默认false不升级
        :type upgrade_run_time: bool
        
        """
        req = self.model_v20180525.UpgradeClusterInstancesRequest()
        req.ClusterId = cluster_id
        req.Operation = operation
        req.UpgradeType = upgrade_type
        req.InstanceIds = instance_ids
        req.ResetParam = reset_param
        req.SkipPreCheck = skip_pre_check
        req.MaxNotReadyPercent = max_not_ready_percent
        req.UpgradeRunTime = upgrade_run_time
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.UpgradeClusterInstances(req)
        return response

    @retry_with_conditions(3, 10)
    def upgrade_cluster_release(self, cluster_id=None, name=None, namespace=None, chart=None, values=None, chart_from=None, chart_version=None, chart_repo_url=None, username=None, password=None, chart_namespace=None, cluster_type=None, **kwargs):
        """升级集群中已安装的应用
        :param cluster_id: 集群ID
        :type cluster_id: str
        :param name: 自定义的应用名称
        :type name: str
        :param namespace: 应用命名空间
        :type namespace: str
        :param chart: 制品名称或从第三方repo 安装chart时，制品压缩包下载地址, 不支持重定向类型chart 地址，结尾为*.tgz
        :type chart: str
        :param values: 自定义参数，覆盖chart 中values.yaml 中的参数
        :type values: :class:`tencentcloud.tke.v20180525.models.Releasevalues`
        :param chartFrom: 制品来源，范围：tke-market 或 other 默认值：tke-market，示例值：tke-market
        :type chartFrom: str
        :param chartVersion: 制品版本( 从第三方安装时，不传这个参数）
        :type chartVersion: str
        :param chartRepoURL: 制品仓库URL地址
        :type chartRepoURL: str
        :param username: 制品访问用户名
        :type username: str
        :param password: 制品访问密码
        :type password: str
        :param chartnamespace: 制品命名空间，chartFrom为tke-market时chartnamespace不为空，值为DescribeProducts接口反馈的namespace
        :type chartnamespace: str
        :param cluster_type: 集群类型，支持传 tke, eks, tkeedge, external(注册集群）
        :type cluster_type: str
        
        """
        req = self.model_v20180525.UpgradeClusterReleaseRequest()
        req.ClusterId = cluster_id
        req.Name = name
        req.Namespace = namespace
        req.Chart = chart
        req.Values = values
        req.ChartFrom = chart_from
        req.ChartVersion = chart_version
        req.ChartRepoURL = chart_repo_url
        req.Username = username
        req.Password = password
        req.ChartNamespace = chart_namespace
        req.ClusterType = cluster_type
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20180525.UpgradeClusterRelease(req)
        return response

    @retry_with_conditions(3, 10)
    def create_health_check_policy(self, cluster_id=None, health_check_policy=None, **kwargs):
        """创建健康检测策略
        :param cluster_id: 集群ID
        :type cluster_id: str
        :param health_check_policy: 健康检测策略
        :type health_check_policy: :class:`tencentcloud.tke.v20220501.models.health_check_policy`
        
        """
        req = self.model_v20220501.CreateHealthCheckPolicyRequest()
        req.ClusterId = cluster_id
        req.HealthCheckPolicy = health_check_policy
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20220501.CreateHealthCheckPolicy(req)
        return response

    @retry_with_conditions(3, 10)
    def create_node_pool(self, cluster_id=None, name=None, type=None, labels=None, taints=None, tags=None, deletion_protection=None, unschedulable=None, native=None, annotations=None, **kwargs):
        """创建 TKE 节点池
        :param cluster_id: 集群 ID
        :type cluster_id: str
        :param name: 节点池名称
        :type name: str
        :param type: 节点池类型
        :type type: str
        :param labels: 节点  labels
        :type labels: list of Label
        :param taints: 节点污点
        :type taints: list of Taint
        :param tags: 节点标签
        :type tags: list of TagSpecification
        :param deletion_protection: 是否开启删除保护
        :type deletion_protection: bool
        :param unschedulable: 节点是否默认不可调度
        :type unschedulable: bool
        :param native: 原生节点池创建参数
        :type native: :class:`tencentcloud.tke.v20220501.models.CreatenativeNodePoolParam`
        :param annotations: 节点 Annotation 列表
        :type annotations: list of Annotation
        
        """
        req = self.model_v20220501.CreateNodePoolRequest()
        req.ClusterId = cluster_id
        req.Name = name
        req.Type = type
        req.Labels = labels
        req.Taints = taints
        req.Tags = tags
        req.DeletionProtection = deletion_protection
        req.Unschedulable = unschedulable
        req.Native = native
        req.Annotations = annotations
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20220501.CreateNodePool(req)
        return response

    @retry_with_conditions(3, 10)
    def delete_health_check_policy(self, cluster_id=None, health_check_policy_name=None, **kwargs):
        """删除健康检测策略
        :param cluster_id: 集群 ID
        :type cluster_id: str
        :param health_check_policy_name: 健康检测策略名称
        :type health_check_policy_name: str
        
        """
        req = self.model_v20220501.DeleteHealthCheckPolicyRequest()
        req.ClusterId = cluster_id
        req.HealthCheckPolicyName = health_check_policy_name
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20220501.DeleteHealthCheckPolicy(req)
        return response

    @retry_with_conditions(3, 10)
    def delete_node_pool(self, cluster_id=None, node_pool_id=None, **kwargs):
        """删除 TKE 节点池
        :param cluster_id: 集群 ID
        :type cluster_id: str
        :param node_pool_id: 节点池 ID
        :type node_pool_id: str
        
        """
        req = self.model_v20220501.DeleteNodePoolRequest()
        req.ClusterId = cluster_id
        req.NodePoolId = node_pool_id
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20220501.DeleteNodePool(req)
        return response

    @retry_with_conditions(3, 10)
    def describe_cluster_instances(self, cluster_id=None, offset=None, limit=None, filters=None, sort_by=None, **kwargs):
        """查询集群下节点实例信息
        :param cluster_id: 集群ID
        :type cluster_id: str
        :param offset: 偏移量，默认为0。关于offset的更进一步介绍请参考 API [简介](https://cloud.tencent.com/document/api/213/15688)中的相关小节。
        :type offset: int
        :param limit: 返回数量，默认为20，最大值为100。关于limit的更进一步介绍请参考 API [简介](https://cloud.tencent.com/document/api/213/15688)中的相关小节。
        :type limit: int
        :param filters: 过滤条件列表:
InstanceIds(实例ID),InstanceType(实例类型：Regular，Native，Super，External),VagueIpAddress(模糊匹配IP),Labels(k8s节点label),NodePoolNames(节点池名称),VagueInstanceName(模糊匹配节点名),InstanceStates(节点状态),Unschedulable(是否封锁),NodePoolIds(节点池ID)
        :type filters: list of Filter
        :param sort_by: 排序信息
        :type sort_by: :class:`tencentcloud.tke.v20220501.models.sort_by`
        
        """
        req = self.model_v20220501.DescribeClusterInstancesRequest()
        req.ClusterId = cluster_id
        req.Offset = offset
        req.Limit = limit
        req.Filters = filters
        req.SortBy = sort_by
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20220501.DescribeClusterInstances(req)
        return response

    @retry_with_conditions(3, 10)
    def describe_health_check_policies(self, cluster_id=None, filters=None, limit=None, offset=None, **kwargs):
        """查询健康检测策略
        :param cluster_id: 集群 ID
        :type cluster_id: str
        :param filters: ·  HealthCheckPolicyName
    按照【健康检测策略名称】进行过滤。
    类型：String
    必选：否
        :type filters: list of Filter
        :param limit: 最大输出条数，默认20，最大为100
        :type limit: int
        :param offset: 偏移量，默认0
        :type offset: int
        
        """
        req = self.model_v20220501.DescribeHealthCheckPoliciesRequest()
        req.ClusterId = cluster_id
        req.Filters = filters
        req.Limit = limit
        req.Offset = offset
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20220501.DescribeHealthCheckPolicies(req)
        return response

    @retry_with_conditions(3, 10)
    def describe_health_check_policy_bindings(self, cluster_id=None, filter=None, limit=None, offset=None, **kwargs):
        """查询健康检测策略绑定关系
        :param cluster_id: 集群 ID
        :type cluster_id: str
        :param filter: ·  HealthCheckPolicyName
    按照【健康检测规则名称】进行过滤。
    类型：String
    必选：否
        :type filter: list of filter
        :param limit: 最大输出条数，默认20，最大为100
        :type limit: int
        :param offset: 偏移量，默认0
        :type offset: int
        
        """
        req = self.model_v20220501.DescribeHealthCheckPolicyBindingsRequest()
        req.ClusterId = cluster_id
        req.Filter = filter
        req.Limit = limit
        req.Offset = offset
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20220501.DescribeHealthCheckPolicyBindings(req)
        return response

    def describe_health_check_template(self, **kwargs):
        """查询健康检测策略模板

        :param request: Request instance for DescribeHealthCheckTemplate.
        :type request: :class:`tencentcloud.tke.v20220501.models.DescribeHealthCheckTemplateRequest`
        :rtype: :class:`tencentcloud.tke.v20220501.models.DescribeHealthCheckTemplateResponse`

        
        """
        req = self.model_v20220501.DescribeHealthCheckTemplateRequest()
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20220501.DescribeHealthCheckTemplate(req)
        return response

    @retry_with_conditions(3, 10)
    def describe_node_pools(self, cluster_id=None, filters=None, offset=None, limit=None, **kwargs):
        """查询 TKE 节点池列表
        :param cluster_id: 集群 ID
        :type cluster_id: str
        :param filters: 查询过滤条件：
·  NodePoolsName
    按照【节点池名】进行过滤。
    类型：String
    必选：否

·  NodePoolsId
    按照【节点池id】进行过滤。
    类型：String
    必选：否

·  tags
    按照【标签键值对】进行过滤。
    类型：String
    必选：否

·  tag:tag-key
    按照【标签键值对】进行过滤。
    类型：String
    必选：否
        :type filters: list of Filter
        :param offset: 偏移量，默认0
        :type offset: int
        :param limit: 最大输出条数，默认20，最大为100
        :type limit: int
        
        """
        req = self.model_v20220501.DescribeNodePoolsRequest()
        req.ClusterId = cluster_id
        req.Filters = filters
        req.Offset = offset
        req.Limit = limit
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20220501.DescribeNodePools(req)
        return response

    @retry_with_conditions(3, 10)
    def modify_health_check_policy(self, cluster_id=None, health_check_policy=None, **kwargs):
        """修改健康检测策略
        :param cluster_id: 集群 ID
        :type cluster_id: str
        :param health_check_policy: 健康检测策略
        :type health_check_policy: :class:`tencentcloud.tke.v20220501.models.health_check_policy`
        
        """
        req = self.model_v20220501.ModifyHealthCheckPolicyRequest()
        req.ClusterId = cluster_id
        req.HealthCheckPolicy = health_check_policy
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20220501.ModifyHealthCheckPolicy(req)
        return response

    @retry_with_conditions(3, 10)
    def modify_node_pool(self, cluster_id=None, node_pool_id=None, name=None, labels=None, taints=None, tags=None, deletion_protection=None, unschedulable=None, native=None, annotations=None, **kwargs):
        """更新 TKE 节点池
        :param cluster_id: 集群 ID
        :type cluster_id: str
        :param node_pool_id: 节点池 ID
        :type node_pool_id: str
        :param name: 节点池名称
        :type name: str
        :param labels: 节点  labels
        :type labels: list of Label
        :param taints: 节点污点
        :type taints: list of Taint
        :param tags: 节点标签
        :type tags: list of TagSpecification
        :param deletion_protection: 是否开启删除保护
        :type deletion_protection: bool
        :param unschedulable: 节点是否不可调度
        :type unschedulable: bool
        :param native: 原生节点池更新参数
        :type native: :class:`tencentcloud.tke.v20220501.models.UpdatenativeNodePoolParam`
        :param annotations: 节点 Annotation 列表
        :type annotations: list of Annotation
        
        """
        req = self.model_v20220501.ModifyNodePoolRequest()
        req.ClusterId = cluster_id
        req.NodePoolId = node_pool_id
        req.Name = name
        req.Labels = labels
        req.Taints = taints
        req.Tags = tags
        req.DeletionProtection = deletion_protection
        req.Unschedulable = unschedulable
        req.Native = native
        req.Annotations = annotations
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20220501.ModifyNodePool(req)
        return response

    @retry_with_conditions(3, 10)
    def reboot_machines(self, cluster_id=None, machine_names=None, stop_type=None, **kwargs):
        """重启原生节点实例
        :param cluster_id: 集群 ID
        :type cluster_id: str
        :param machine_names: 节点名字列表，一次请求，传入节点数量上限为100个
        :type machine_names: list of str
        :param stop_type: 实例的关闭模式。取值范围：
soft_first：表示在正常关闭失败后进行强制关闭
hard：直接强制关闭
soft：仅软关机默认取值：soft。
        :type stop_type: str
        
        """
        req = self.model_v20220501.RebootMachinesRequest()
        req.ClusterId = cluster_id
        req.MachineNames = machine_names
        req.StopType = stop_type
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20220501.RebootMachines(req)
        return response

    @retry_with_conditions(3, 10)
    def start_machines(self, cluster_id=None, machine_names=None, **kwargs):
        """本接口 (StartMachines) 用于启动一个或多个原生节点实例。
        :param cluster_id: 集群 ID
        :type cluster_id: str
        :param machine_names: 节点名字列表，一次请求，传入节点数量上限为100个
        :type machine_names: list of str
        
        """
        req = self.model_v20220501.StartMachinesRequest()
        req.ClusterId = cluster_id
        req.MachineNames = machine_names
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20220501.StartMachines(req)
        return response

    @retry_with_conditions(3, 10)
    def stop_machines(self, cluster_id=None, machine_names=None, stop_type=None, **kwargs):
        """本接口 (StopMachines) 用于关闭一个或多个原生节点实例。
        :param cluster_id: 集群 ID
        :type cluster_id: str
        :param machine_names: 节点名字列表，一次请求，传入节点数量上限为100个
        :type machine_names: list of str
        :param stop_type: 实例的关闭模式。取值范围：
        soft_first：表示在正常关闭失败后进行强制关闭
        hard：直接强制关闭
        soft：仅软关机
        :type stop_type: str
        
        """
        req = self.model_v20220501.StopMachinesRequest()
        req.ClusterId = cluster_id
        req.MachineNames = machine_names
        req.StopType = stop_type
        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_v20220501.StopMachines(req)
        return response
