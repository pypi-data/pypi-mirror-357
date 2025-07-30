r'''
# Must CDK for common pattern
'''
from pkgutil import extend_path
__path__ = extend_path(__path__, __name__)

import abc
import builtins
import datetime
import enum
import typing

import jsii
import publication
import typing_extensions

import typeguard
from importlib.metadata import version as _metadata_package_version
TYPEGUARD_MAJOR_VERSION = int(_metadata_package_version('typeguard').split('.')[0])

def check_type(argname: str, value: object, expected_type: typing.Any) -> typing.Any:
    if TYPEGUARD_MAJOR_VERSION <= 2:
        return typeguard.check_type(argname=argname, value=value, expected_type=expected_type) # type:ignore
    else:
        if isinstance(value, jsii._reference_map.InterfaceDynamicProxy): # pyright: ignore [reportAttributeAccessIssue]
           pass
        else:
            if TYPEGUARD_MAJOR_VERSION == 3:
                typeguard.config.collection_check_strategy = typeguard.CollectionCheckStrategy.ALL_ITEMS # type:ignore
                typeguard.check_type(value=value, expected_type=expected_type) # type:ignore
            else:
                typeguard.check_type(value=value, expected_type=expected_type, collection_check_strategy=typeguard.CollectionCheckStrategy.ALL_ITEMS) # type:ignore

from ._jsii import *

import aws_cdk.aws_apigateway as _aws_cdk_aws_apigateway_ceddda9d
import aws_cdk.aws_certificatemanager as _aws_cdk_aws_certificatemanager_ceddda9d
import aws_cdk.aws_ec2 as _aws_cdk_aws_ec2_ceddda9d
import aws_cdk.aws_ecs as _aws_cdk_aws_ecs_ceddda9d
import aws_cdk.aws_elasticloadbalancingv2 as _aws_cdk_aws_elasticloadbalancingv2_ceddda9d
import aws_cdk.aws_iam as _aws_cdk_aws_iam_ceddda9d
import aws_cdk.aws_lambda as _aws_cdk_aws_lambda_ceddda9d
import aws_cdk.aws_logs as _aws_cdk_aws_logs_ceddda9d
import aws_cdk.aws_route53 as _aws_cdk_aws_route53_ceddda9d
import constructs as _constructs_77d1e7e8


class ApiGatewayToLambdaCustomDomain(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="must-cdk.ApiGatewayToLambdaCustomDomain",
):
    '''
    :summary: The ApiGatewayToLambda class.
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        api_gateway_props: typing.Any = None,
        create_usage_plan: typing.Optional[builtins.bool] = None,
        custom_domain_name: typing.Optional[builtins.str] = None,
        existing_lambda_obj: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.Function] = None,
        hosted_zone: typing.Optional[_aws_cdk_aws_route53_ceddda9d.IHostedZone] = None,
        lambda_function_props: typing.Optional[typing.Union[_aws_cdk_aws_lambda_ceddda9d.FunctionProps, typing.Dict[builtins.str, typing.Any]]] = None,
        log_group_props: typing.Optional[typing.Union[_aws_cdk_aws_logs_ceddda9d.LogGroupProps, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param scope: - represents the scope for all the resources.
        :param id: - this is a a scope-unique id.
        :param api_gateway_props: Optional user-provided props to override the default props for the API.
        :param create_usage_plan: Whether to create a Usage Plan attached to the API. Must be true if apiGatewayProps.defaultMethodOptions.apiKeyRequired is true
        :param custom_domain_name: Optional custom domain name for API Gateway, an ACM cert will also created. Default: - no custom domain
        :param existing_lambda_obj: Existing instance of Lambda Function object, providing both this and ``lambdaFunctionProps`` will cause an error. Default: - None
        :param hosted_zone: Optional Route53 hosted zone to create alias record for the custom domain. Default: - no Route53 alias record created
        :param lambda_function_props: User provided props to override the default props for the Lambda function.
        :param log_group_props: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d7036b176aa7b446813bdbc7672055bba27972db6a947684b57c6f8f02e0f9b6)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = ApiGatewayToLambdaProps(
            api_gateway_props=api_gateway_props,
            create_usage_plan=create_usage_plan,
            custom_domain_name=custom_domain_name,
            existing_lambda_obj=existing_lambda_obj,
            hosted_zone=hosted_zone,
            lambda_function_props=lambda_function_props,
            log_group_props=log_group_props,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property
    @jsii.member(jsii_name="apiGateway")
    def api_gateway(self) -> _aws_cdk_aws_apigateway_ceddda9d.RestApi:
        return typing.cast(_aws_cdk_aws_apigateway_ceddda9d.RestApi, jsii.get(self, "apiGateway"))

    @builtins.property
    @jsii.member(jsii_name="apiGatewayLogGroup")
    def api_gateway_log_group(self) -> _aws_cdk_aws_logs_ceddda9d.LogGroup:
        return typing.cast(_aws_cdk_aws_logs_ceddda9d.LogGroup, jsii.get(self, "apiGatewayLogGroup"))

    @builtins.property
    @jsii.member(jsii_name="lambdaFunction")
    def lambda_function(self) -> _aws_cdk_aws_lambda_ceddda9d.Function:
        return typing.cast(_aws_cdk_aws_lambda_ceddda9d.Function, jsii.get(self, "lambdaFunction"))

    @builtins.property
    @jsii.member(jsii_name="apiGatewayCloudWatchRole")
    def api_gateway_cloud_watch_role(
        self,
    ) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.Role]:
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.Role], jsii.get(self, "apiGatewayCloudWatchRole"))

    @builtins.property
    @jsii.member(jsii_name="aRecord")
    def a_record(self) -> typing.Optional[_aws_cdk_aws_route53_ceddda9d.ARecord]:
        return typing.cast(typing.Optional[_aws_cdk_aws_route53_ceddda9d.ARecord], jsii.get(self, "aRecord"))

    @builtins.property
    @jsii.member(jsii_name="certificate")
    def certificate(
        self,
    ) -> typing.Optional[_aws_cdk_aws_certificatemanager_ceddda9d.Certificate]:
        return typing.cast(typing.Optional[_aws_cdk_aws_certificatemanager_ceddda9d.Certificate], jsii.get(self, "certificate"))

    @builtins.property
    @jsii.member(jsii_name="domain")
    def domain(self) -> typing.Optional[_aws_cdk_aws_apigateway_ceddda9d.DomainName]:
        return typing.cast(typing.Optional[_aws_cdk_aws_apigateway_ceddda9d.DomainName], jsii.get(self, "domain"))


@jsii.data_type(
    jsii_type="must-cdk.ApiGatewayToLambdaProps",
    jsii_struct_bases=[],
    name_mapping={
        "api_gateway_props": "apiGatewayProps",
        "create_usage_plan": "createUsagePlan",
        "custom_domain_name": "customDomainName",
        "existing_lambda_obj": "existingLambdaObj",
        "hosted_zone": "hostedZone",
        "lambda_function_props": "lambdaFunctionProps",
        "log_group_props": "logGroupProps",
    },
)
class ApiGatewayToLambdaProps:
    def __init__(
        self,
        *,
        api_gateway_props: typing.Any = None,
        create_usage_plan: typing.Optional[builtins.bool] = None,
        custom_domain_name: typing.Optional[builtins.str] = None,
        existing_lambda_obj: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.Function] = None,
        hosted_zone: typing.Optional[_aws_cdk_aws_route53_ceddda9d.IHostedZone] = None,
        lambda_function_props: typing.Optional[typing.Union[_aws_cdk_aws_lambda_ceddda9d.FunctionProps, typing.Dict[builtins.str, typing.Any]]] = None,
        log_group_props: typing.Optional[typing.Union[_aws_cdk_aws_logs_ceddda9d.LogGroupProps, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param api_gateway_props: Optional user-provided props to override the default props for the API.
        :param create_usage_plan: Whether to create a Usage Plan attached to the API. Must be true if apiGatewayProps.defaultMethodOptions.apiKeyRequired is true
        :param custom_domain_name: Optional custom domain name for API Gateway, an ACM cert will also created. Default: - no custom domain
        :param existing_lambda_obj: Existing instance of Lambda Function object, providing both this and ``lambdaFunctionProps`` will cause an error. Default: - None
        :param hosted_zone: Optional Route53 hosted zone to create alias record for the custom domain. Default: - no Route53 alias record created
        :param lambda_function_props: User provided props to override the default props for the Lambda function.
        :param log_group_props: 
        '''
        if isinstance(lambda_function_props, dict):
            lambda_function_props = _aws_cdk_aws_lambda_ceddda9d.FunctionProps(**lambda_function_props)
        if isinstance(log_group_props, dict):
            log_group_props = _aws_cdk_aws_logs_ceddda9d.LogGroupProps(**log_group_props)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7c51143b7da8fc50ffd3240aae88642c332f9ccc1136e275abf9d1065df7ea17)
            check_type(argname="argument api_gateway_props", value=api_gateway_props, expected_type=type_hints["api_gateway_props"])
            check_type(argname="argument create_usage_plan", value=create_usage_plan, expected_type=type_hints["create_usage_plan"])
            check_type(argname="argument custom_domain_name", value=custom_domain_name, expected_type=type_hints["custom_domain_name"])
            check_type(argname="argument existing_lambda_obj", value=existing_lambda_obj, expected_type=type_hints["existing_lambda_obj"])
            check_type(argname="argument hosted_zone", value=hosted_zone, expected_type=type_hints["hosted_zone"])
            check_type(argname="argument lambda_function_props", value=lambda_function_props, expected_type=type_hints["lambda_function_props"])
            check_type(argname="argument log_group_props", value=log_group_props, expected_type=type_hints["log_group_props"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if api_gateway_props is not None:
            self._values["api_gateway_props"] = api_gateway_props
        if create_usage_plan is not None:
            self._values["create_usage_plan"] = create_usage_plan
        if custom_domain_name is not None:
            self._values["custom_domain_name"] = custom_domain_name
        if existing_lambda_obj is not None:
            self._values["existing_lambda_obj"] = existing_lambda_obj
        if hosted_zone is not None:
            self._values["hosted_zone"] = hosted_zone
        if lambda_function_props is not None:
            self._values["lambda_function_props"] = lambda_function_props
        if log_group_props is not None:
            self._values["log_group_props"] = log_group_props

    @builtins.property
    def api_gateway_props(self) -> typing.Any:
        '''Optional user-provided props to override the default props for the API.'''
        result = self._values.get("api_gateway_props")
        return typing.cast(typing.Any, result)

    @builtins.property
    def create_usage_plan(self) -> typing.Optional[builtins.bool]:
        '''Whether to create a Usage Plan attached to the API.

        Must be true if
        apiGatewayProps.defaultMethodOptions.apiKeyRequired is true
        '''
        result = self._values.get("create_usage_plan")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def custom_domain_name(self) -> typing.Optional[builtins.str]:
        '''Optional custom domain name for API Gateway, an ACM cert will also created.

        :default: - no custom domain
        '''
        result = self._values.get("custom_domain_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def existing_lambda_obj(
        self,
    ) -> typing.Optional[_aws_cdk_aws_lambda_ceddda9d.Function]:
        '''Existing instance of Lambda Function object, providing both this and ``lambdaFunctionProps`` will cause an error.

        :default: - None
        '''
        result = self._values.get("existing_lambda_obj")
        return typing.cast(typing.Optional[_aws_cdk_aws_lambda_ceddda9d.Function], result)

    @builtins.property
    def hosted_zone(self) -> typing.Optional[_aws_cdk_aws_route53_ceddda9d.IHostedZone]:
        '''Optional Route53 hosted zone to create alias record for the custom domain.

        :default: - no Route53 alias record created
        '''
        result = self._values.get("hosted_zone")
        return typing.cast(typing.Optional[_aws_cdk_aws_route53_ceddda9d.IHostedZone], result)

    @builtins.property
    def lambda_function_props(
        self,
    ) -> typing.Optional[_aws_cdk_aws_lambda_ceddda9d.FunctionProps]:
        '''User provided props to override the default props for the Lambda function.'''
        result = self._values.get("lambda_function_props")
        return typing.cast(typing.Optional[_aws_cdk_aws_lambda_ceddda9d.FunctionProps], result)

    @builtins.property
    def log_group_props(
        self,
    ) -> typing.Optional[_aws_cdk_aws_logs_ceddda9d.LogGroupProps]:
        result = self._values.get("log_group_props")
        return typing.cast(typing.Optional[_aws_cdk_aws_logs_ceddda9d.LogGroupProps], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ApiGatewayToLambdaProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="must-cdk.AutoScalingProps",
    jsii_struct_bases=[],
    name_mapping={
        "max_capacity": "maxCapacity",
        "min_capacity": "minCapacity",
        "target_cpu_utilization_percent": "targetCpuUtilizationPercent",
        "scale_in_cooldown_sec": "scaleInCooldownSec",
        "scale_out_cooldown_sec": "scaleOutCooldownSec",
    },
)
class AutoScalingProps:
    def __init__(
        self,
        *,
        max_capacity: jsii.Number,
        min_capacity: jsii.Number,
        target_cpu_utilization_percent: jsii.Number,
        scale_in_cooldown_sec: typing.Optional[jsii.Number] = None,
        scale_out_cooldown_sec: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''Configuration for ECS service autoscaling.

        :param max_capacity: Maximum number of tasks.
        :param min_capacity: Minimum number of tasks.
        :param target_cpu_utilization_percent: Target CPU utilization percentage.
        :param scale_in_cooldown_sec: Cooldown time in seconds after scale-in.
        :param scale_out_cooldown_sec: Cooldown time in seconds after scale-out.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d0ea30b15daf73de785b4991457443ee0ca220224fbd08155a17d86c67413930)
            check_type(argname="argument max_capacity", value=max_capacity, expected_type=type_hints["max_capacity"])
            check_type(argname="argument min_capacity", value=min_capacity, expected_type=type_hints["min_capacity"])
            check_type(argname="argument target_cpu_utilization_percent", value=target_cpu_utilization_percent, expected_type=type_hints["target_cpu_utilization_percent"])
            check_type(argname="argument scale_in_cooldown_sec", value=scale_in_cooldown_sec, expected_type=type_hints["scale_in_cooldown_sec"])
            check_type(argname="argument scale_out_cooldown_sec", value=scale_out_cooldown_sec, expected_type=type_hints["scale_out_cooldown_sec"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "max_capacity": max_capacity,
            "min_capacity": min_capacity,
            "target_cpu_utilization_percent": target_cpu_utilization_percent,
        }
        if scale_in_cooldown_sec is not None:
            self._values["scale_in_cooldown_sec"] = scale_in_cooldown_sec
        if scale_out_cooldown_sec is not None:
            self._values["scale_out_cooldown_sec"] = scale_out_cooldown_sec

    @builtins.property
    def max_capacity(self) -> jsii.Number:
        '''Maximum number of tasks.'''
        result = self._values.get("max_capacity")
        assert result is not None, "Required property 'max_capacity' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def min_capacity(self) -> jsii.Number:
        '''Minimum number of tasks.'''
        result = self._values.get("min_capacity")
        assert result is not None, "Required property 'min_capacity' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def target_cpu_utilization_percent(self) -> jsii.Number:
        '''Target CPU utilization percentage.'''
        result = self._values.get("target_cpu_utilization_percent")
        assert result is not None, "Required property 'target_cpu_utilization_percent' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def scale_in_cooldown_sec(self) -> typing.Optional[jsii.Number]:
        '''Cooldown time in seconds after scale-in.'''
        result = self._values.get("scale_in_cooldown_sec")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def scale_out_cooldown_sec(self) -> typing.Optional[jsii.Number]:
        '''Cooldown time in seconds after scale-out.'''
        result = self._values.get("scale_out_cooldown_sec")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AutoScalingProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class EcsCodeDeploy(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="must-cdk.EcsCodeDeploy",
):
    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        certificate_arn: builtins.str,
        cluster: _aws_cdk_aws_ecs_ceddda9d.ICluster,
        container_port: jsii.Number,
        environment: builtins.str,
        image_uri: builtins.str,
        service_name: builtins.str,
        vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
        auto_scaling: typing.Optional[typing.Union[AutoScalingProps, typing.Dict[builtins.str, typing.Any]]] = None,
        enable_public_load_balancer: typing.Optional[builtins.bool] = None,
        health_check: typing.Optional[typing.Union[_aws_cdk_aws_ecs_ceddda9d.HealthCheck, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param certificate_arn: 
        :param cluster: 
        :param container_port: 
        :param environment: 
        :param image_uri: 
        :param service_name: 
        :param vpc: 
        :param auto_scaling: 
        :param enable_public_load_balancer: 
        :param health_check: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__19ac4f77d3bba1391929b87d2d23b70fe61e21aa6809f43ed4283d6ecf350909)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = EcsCodeDeployProps(
            certificate_arn=certificate_arn,
            cluster=cluster,
            container_port=container_port,
            environment=environment,
            image_uri=image_uri,
            service_name=service_name,
            vpc=vpc,
            auto_scaling=auto_scaling,
            enable_public_load_balancer=enable_public_load_balancer,
            health_check=health_check,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property
    @jsii.member(jsii_name="loadBalancer")
    def load_balancer(
        self,
    ) -> _aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ApplicationLoadBalancer:
        return typing.cast(_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ApplicationLoadBalancer, jsii.get(self, "loadBalancer"))

    @builtins.property
    @jsii.member(jsii_name="service")
    def service(self) -> _aws_cdk_aws_ecs_ceddda9d.FargateService:
        return typing.cast(_aws_cdk_aws_ecs_ceddda9d.FargateService, jsii.get(self, "service"))

    @builtins.property
    @jsii.member(jsii_name="taskRole")
    def task_role(self) -> _aws_cdk_aws_iam_ceddda9d.Role:
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.Role, jsii.get(self, "taskRole"))

    @task_role.setter
    def task_role(self, value: _aws_cdk_aws_iam_ceddda9d.Role) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__60923688f982908f977f559dbd1295485a3b0547df3c45291a862130dede0c3e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "taskRole", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="must-cdk.EcsCodeDeployProps",
    jsii_struct_bases=[],
    name_mapping={
        "certificate_arn": "certificateArn",
        "cluster": "cluster",
        "container_port": "containerPort",
        "environment": "environment",
        "image_uri": "imageUri",
        "service_name": "serviceName",
        "vpc": "vpc",
        "auto_scaling": "autoScaling",
        "enable_public_load_balancer": "enablePublicLoadBalancer",
        "health_check": "healthCheck",
    },
)
class EcsCodeDeployProps:
    def __init__(
        self,
        *,
        certificate_arn: builtins.str,
        cluster: _aws_cdk_aws_ecs_ceddda9d.ICluster,
        container_port: jsii.Number,
        environment: builtins.str,
        image_uri: builtins.str,
        service_name: builtins.str,
        vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
        auto_scaling: typing.Optional[typing.Union[AutoScalingProps, typing.Dict[builtins.str, typing.Any]]] = None,
        enable_public_load_balancer: typing.Optional[builtins.bool] = None,
        health_check: typing.Optional[typing.Union[_aws_cdk_aws_ecs_ceddda9d.HealthCheck, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param certificate_arn: 
        :param cluster: 
        :param container_port: 
        :param environment: 
        :param image_uri: 
        :param service_name: 
        :param vpc: 
        :param auto_scaling: 
        :param enable_public_load_balancer: 
        :param health_check: 
        '''
        if isinstance(auto_scaling, dict):
            auto_scaling = AutoScalingProps(**auto_scaling)
        if isinstance(health_check, dict):
            health_check = _aws_cdk_aws_ecs_ceddda9d.HealthCheck(**health_check)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0e1edfc306738ea99e0bd03a55876d7f75a063970dd3103fc1bbb766dff014b1)
            check_type(argname="argument certificate_arn", value=certificate_arn, expected_type=type_hints["certificate_arn"])
            check_type(argname="argument cluster", value=cluster, expected_type=type_hints["cluster"])
            check_type(argname="argument container_port", value=container_port, expected_type=type_hints["container_port"])
            check_type(argname="argument environment", value=environment, expected_type=type_hints["environment"])
            check_type(argname="argument image_uri", value=image_uri, expected_type=type_hints["image_uri"])
            check_type(argname="argument service_name", value=service_name, expected_type=type_hints["service_name"])
            check_type(argname="argument vpc", value=vpc, expected_type=type_hints["vpc"])
            check_type(argname="argument auto_scaling", value=auto_scaling, expected_type=type_hints["auto_scaling"])
            check_type(argname="argument enable_public_load_balancer", value=enable_public_load_balancer, expected_type=type_hints["enable_public_load_balancer"])
            check_type(argname="argument health_check", value=health_check, expected_type=type_hints["health_check"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "certificate_arn": certificate_arn,
            "cluster": cluster,
            "container_port": container_port,
            "environment": environment,
            "image_uri": image_uri,
            "service_name": service_name,
            "vpc": vpc,
        }
        if auto_scaling is not None:
            self._values["auto_scaling"] = auto_scaling
        if enable_public_load_balancer is not None:
            self._values["enable_public_load_balancer"] = enable_public_load_balancer
        if health_check is not None:
            self._values["health_check"] = health_check

    @builtins.property
    def certificate_arn(self) -> builtins.str:
        result = self._values.get("certificate_arn")
        assert result is not None, "Required property 'certificate_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def cluster(self) -> _aws_cdk_aws_ecs_ceddda9d.ICluster:
        result = self._values.get("cluster")
        assert result is not None, "Required property 'cluster' is missing"
        return typing.cast(_aws_cdk_aws_ecs_ceddda9d.ICluster, result)

    @builtins.property
    def container_port(self) -> jsii.Number:
        result = self._values.get("container_port")
        assert result is not None, "Required property 'container_port' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def environment(self) -> builtins.str:
        result = self._values.get("environment")
        assert result is not None, "Required property 'environment' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def image_uri(self) -> builtins.str:
        result = self._values.get("image_uri")
        assert result is not None, "Required property 'image_uri' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def service_name(self) -> builtins.str:
        result = self._values.get("service_name")
        assert result is not None, "Required property 'service_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def vpc(self) -> _aws_cdk_aws_ec2_ceddda9d.IVpc:
        result = self._values.get("vpc")
        assert result is not None, "Required property 'vpc' is missing"
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.IVpc, result)

    @builtins.property
    def auto_scaling(self) -> typing.Optional[AutoScalingProps]:
        result = self._values.get("auto_scaling")
        return typing.cast(typing.Optional[AutoScalingProps], result)

    @builtins.property
    def enable_public_load_balancer(self) -> typing.Optional[builtins.bool]:
        result = self._values.get("enable_public_load_balancer")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def health_check(self) -> typing.Optional[_aws_cdk_aws_ecs_ceddda9d.HealthCheck]:
        result = self._values.get("health_check")
        return typing.cast(typing.Optional[_aws_cdk_aws_ecs_ceddda9d.HealthCheck], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "EcsCodeDeployProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class WebsocketApiGatewayToLambdaCustomDomain(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="must-cdk.WebsocketApiGatewayToLambdaCustomDomain",
):
    '''
    :summary: The ApiGatewayToLambda class.
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        api_gateway_props: typing.Any = None,
        create_usage_plan: typing.Optional[builtins.bool] = None,
        custom_domain_name: typing.Optional[builtins.str] = None,
        existing_lambda_obj: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.Function] = None,
        hosted_zone: typing.Optional[_aws_cdk_aws_route53_ceddda9d.IHostedZone] = None,
        lambda_function_props: typing.Optional[typing.Union[_aws_cdk_aws_lambda_ceddda9d.FunctionProps, typing.Dict[builtins.str, typing.Any]]] = None,
        log_group_props: typing.Optional[typing.Union[_aws_cdk_aws_logs_ceddda9d.LogGroupProps, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param scope: - represents the scope for all the resources.
        :param id: - this is a a scope-unique id.
        :param api_gateway_props: Optional user-provided props to override the default props for the API.
        :param create_usage_plan: Whether to create a Usage Plan attached to the API. Must be true if apiGatewayProps.defaultMethodOptions.apiKeyRequired is true
        :param custom_domain_name: Optional custom domain name for API Gateway, an ACM cert will also created. Default: - no custom domain
        :param existing_lambda_obj: Existing instance of Lambda Function object, providing both this and ``lambdaFunctionProps`` will cause an error. Default: - None
        :param hosted_zone: Optional Route53 hosted zone to create alias record for the custom domain. Default: - no Route53 alias record created
        :param lambda_function_props: User provided props to override the default props for the Lambda function.
        :param log_group_props: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__448d9aeeae459df879203fad12fb34ff1b12039929f0a465891bedcfc130f38c)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = WebsocketApiGatewayToLambdaProps(
            api_gateway_props=api_gateway_props,
            create_usage_plan=create_usage_plan,
            custom_domain_name=custom_domain_name,
            existing_lambda_obj=existing_lambda_obj,
            hosted_zone=hosted_zone,
            lambda_function_props=lambda_function_props,
            log_group_props=log_group_props,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property
    @jsii.member(jsii_name="apiGateway")
    def api_gateway(self) -> _aws_cdk_aws_apigateway_ceddda9d.RestApi:
        return typing.cast(_aws_cdk_aws_apigateway_ceddda9d.RestApi, jsii.get(self, "apiGateway"))

    @builtins.property
    @jsii.member(jsii_name="apiGatewayLogGroup")
    def api_gateway_log_group(self) -> _aws_cdk_aws_logs_ceddda9d.LogGroup:
        return typing.cast(_aws_cdk_aws_logs_ceddda9d.LogGroup, jsii.get(self, "apiGatewayLogGroup"))

    @builtins.property
    @jsii.member(jsii_name="lambdaFunction")
    def lambda_function(self) -> _aws_cdk_aws_lambda_ceddda9d.Function:
        return typing.cast(_aws_cdk_aws_lambda_ceddda9d.Function, jsii.get(self, "lambdaFunction"))

    @builtins.property
    @jsii.member(jsii_name="apiGatewayCloudWatchRole")
    def api_gateway_cloud_watch_role(
        self,
    ) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.Role]:
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.Role], jsii.get(self, "apiGatewayCloudWatchRole"))

    @builtins.property
    @jsii.member(jsii_name="aRecord")
    def a_record(self) -> typing.Optional[_aws_cdk_aws_route53_ceddda9d.ARecord]:
        return typing.cast(typing.Optional[_aws_cdk_aws_route53_ceddda9d.ARecord], jsii.get(self, "aRecord"))

    @builtins.property
    @jsii.member(jsii_name="certificate")
    def certificate(
        self,
    ) -> typing.Optional[_aws_cdk_aws_certificatemanager_ceddda9d.Certificate]:
        return typing.cast(typing.Optional[_aws_cdk_aws_certificatemanager_ceddda9d.Certificate], jsii.get(self, "certificate"))

    @builtins.property
    @jsii.member(jsii_name="domain")
    def domain(self) -> typing.Optional[_aws_cdk_aws_apigateway_ceddda9d.DomainName]:
        return typing.cast(typing.Optional[_aws_cdk_aws_apigateway_ceddda9d.DomainName], jsii.get(self, "domain"))


@jsii.data_type(
    jsii_type="must-cdk.WebsocketApiGatewayToLambdaProps",
    jsii_struct_bases=[],
    name_mapping={
        "api_gateway_props": "apiGatewayProps",
        "create_usage_plan": "createUsagePlan",
        "custom_domain_name": "customDomainName",
        "existing_lambda_obj": "existingLambdaObj",
        "hosted_zone": "hostedZone",
        "lambda_function_props": "lambdaFunctionProps",
        "log_group_props": "logGroupProps",
    },
)
class WebsocketApiGatewayToLambdaProps:
    def __init__(
        self,
        *,
        api_gateway_props: typing.Any = None,
        create_usage_plan: typing.Optional[builtins.bool] = None,
        custom_domain_name: typing.Optional[builtins.str] = None,
        existing_lambda_obj: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.Function] = None,
        hosted_zone: typing.Optional[_aws_cdk_aws_route53_ceddda9d.IHostedZone] = None,
        lambda_function_props: typing.Optional[typing.Union[_aws_cdk_aws_lambda_ceddda9d.FunctionProps, typing.Dict[builtins.str, typing.Any]]] = None,
        log_group_props: typing.Optional[typing.Union[_aws_cdk_aws_logs_ceddda9d.LogGroupProps, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param api_gateway_props: Optional user-provided props to override the default props for the API.
        :param create_usage_plan: Whether to create a Usage Plan attached to the API. Must be true if apiGatewayProps.defaultMethodOptions.apiKeyRequired is true
        :param custom_domain_name: Optional custom domain name for API Gateway, an ACM cert will also created. Default: - no custom domain
        :param existing_lambda_obj: Existing instance of Lambda Function object, providing both this and ``lambdaFunctionProps`` will cause an error. Default: - None
        :param hosted_zone: Optional Route53 hosted zone to create alias record for the custom domain. Default: - no Route53 alias record created
        :param lambda_function_props: User provided props to override the default props for the Lambda function.
        :param log_group_props: 
        '''
        if isinstance(lambda_function_props, dict):
            lambda_function_props = _aws_cdk_aws_lambda_ceddda9d.FunctionProps(**lambda_function_props)
        if isinstance(log_group_props, dict):
            log_group_props = _aws_cdk_aws_logs_ceddda9d.LogGroupProps(**log_group_props)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__109c686be15dfacf97f31b8340ac53463b8369382aaf60b63405ca329516af4d)
            check_type(argname="argument api_gateway_props", value=api_gateway_props, expected_type=type_hints["api_gateway_props"])
            check_type(argname="argument create_usage_plan", value=create_usage_plan, expected_type=type_hints["create_usage_plan"])
            check_type(argname="argument custom_domain_name", value=custom_domain_name, expected_type=type_hints["custom_domain_name"])
            check_type(argname="argument existing_lambda_obj", value=existing_lambda_obj, expected_type=type_hints["existing_lambda_obj"])
            check_type(argname="argument hosted_zone", value=hosted_zone, expected_type=type_hints["hosted_zone"])
            check_type(argname="argument lambda_function_props", value=lambda_function_props, expected_type=type_hints["lambda_function_props"])
            check_type(argname="argument log_group_props", value=log_group_props, expected_type=type_hints["log_group_props"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if api_gateway_props is not None:
            self._values["api_gateway_props"] = api_gateway_props
        if create_usage_plan is not None:
            self._values["create_usage_plan"] = create_usage_plan
        if custom_domain_name is not None:
            self._values["custom_domain_name"] = custom_domain_name
        if existing_lambda_obj is not None:
            self._values["existing_lambda_obj"] = existing_lambda_obj
        if hosted_zone is not None:
            self._values["hosted_zone"] = hosted_zone
        if lambda_function_props is not None:
            self._values["lambda_function_props"] = lambda_function_props
        if log_group_props is not None:
            self._values["log_group_props"] = log_group_props

    @builtins.property
    def api_gateway_props(self) -> typing.Any:
        '''Optional user-provided props to override the default props for the API.'''
        result = self._values.get("api_gateway_props")
        return typing.cast(typing.Any, result)

    @builtins.property
    def create_usage_plan(self) -> typing.Optional[builtins.bool]:
        '''Whether to create a Usage Plan attached to the API.

        Must be true if
        apiGatewayProps.defaultMethodOptions.apiKeyRequired is true
        '''
        result = self._values.get("create_usage_plan")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def custom_domain_name(self) -> typing.Optional[builtins.str]:
        '''Optional custom domain name for API Gateway, an ACM cert will also created.

        :default: - no custom domain
        '''
        result = self._values.get("custom_domain_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def existing_lambda_obj(
        self,
    ) -> typing.Optional[_aws_cdk_aws_lambda_ceddda9d.Function]:
        '''Existing instance of Lambda Function object, providing both this and ``lambdaFunctionProps`` will cause an error.

        :default: - None
        '''
        result = self._values.get("existing_lambda_obj")
        return typing.cast(typing.Optional[_aws_cdk_aws_lambda_ceddda9d.Function], result)

    @builtins.property
    def hosted_zone(self) -> typing.Optional[_aws_cdk_aws_route53_ceddda9d.IHostedZone]:
        '''Optional Route53 hosted zone to create alias record for the custom domain.

        :default: - no Route53 alias record created
        '''
        result = self._values.get("hosted_zone")
        return typing.cast(typing.Optional[_aws_cdk_aws_route53_ceddda9d.IHostedZone], result)

    @builtins.property
    def lambda_function_props(
        self,
    ) -> typing.Optional[_aws_cdk_aws_lambda_ceddda9d.FunctionProps]:
        '''User provided props to override the default props for the Lambda function.'''
        result = self._values.get("lambda_function_props")
        return typing.cast(typing.Optional[_aws_cdk_aws_lambda_ceddda9d.FunctionProps], result)

    @builtins.property
    def log_group_props(
        self,
    ) -> typing.Optional[_aws_cdk_aws_logs_ceddda9d.LogGroupProps]:
        result = self._values.get("log_group_props")
        return typing.cast(typing.Optional[_aws_cdk_aws_logs_ceddda9d.LogGroupProps], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WebsocketApiGatewayToLambdaProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "ApiGatewayToLambdaCustomDomain",
    "ApiGatewayToLambdaProps",
    "AutoScalingProps",
    "EcsCodeDeploy",
    "EcsCodeDeployProps",
    "WebsocketApiGatewayToLambdaCustomDomain",
    "WebsocketApiGatewayToLambdaProps",
]

publication.publish()

def _typecheckingstub__d7036b176aa7b446813bdbc7672055bba27972db6a947684b57c6f8f02e0f9b6(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    api_gateway_props: typing.Any = None,
    create_usage_plan: typing.Optional[builtins.bool] = None,
    custom_domain_name: typing.Optional[builtins.str] = None,
    existing_lambda_obj: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.Function] = None,
    hosted_zone: typing.Optional[_aws_cdk_aws_route53_ceddda9d.IHostedZone] = None,
    lambda_function_props: typing.Optional[typing.Union[_aws_cdk_aws_lambda_ceddda9d.FunctionProps, typing.Dict[builtins.str, typing.Any]]] = None,
    log_group_props: typing.Optional[typing.Union[_aws_cdk_aws_logs_ceddda9d.LogGroupProps, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7c51143b7da8fc50ffd3240aae88642c332f9ccc1136e275abf9d1065df7ea17(
    *,
    api_gateway_props: typing.Any = None,
    create_usage_plan: typing.Optional[builtins.bool] = None,
    custom_domain_name: typing.Optional[builtins.str] = None,
    existing_lambda_obj: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.Function] = None,
    hosted_zone: typing.Optional[_aws_cdk_aws_route53_ceddda9d.IHostedZone] = None,
    lambda_function_props: typing.Optional[typing.Union[_aws_cdk_aws_lambda_ceddda9d.FunctionProps, typing.Dict[builtins.str, typing.Any]]] = None,
    log_group_props: typing.Optional[typing.Union[_aws_cdk_aws_logs_ceddda9d.LogGroupProps, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d0ea30b15daf73de785b4991457443ee0ca220224fbd08155a17d86c67413930(
    *,
    max_capacity: jsii.Number,
    min_capacity: jsii.Number,
    target_cpu_utilization_percent: jsii.Number,
    scale_in_cooldown_sec: typing.Optional[jsii.Number] = None,
    scale_out_cooldown_sec: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__19ac4f77d3bba1391929b87d2d23b70fe61e21aa6809f43ed4283d6ecf350909(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    certificate_arn: builtins.str,
    cluster: _aws_cdk_aws_ecs_ceddda9d.ICluster,
    container_port: jsii.Number,
    environment: builtins.str,
    image_uri: builtins.str,
    service_name: builtins.str,
    vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
    auto_scaling: typing.Optional[typing.Union[AutoScalingProps, typing.Dict[builtins.str, typing.Any]]] = None,
    enable_public_load_balancer: typing.Optional[builtins.bool] = None,
    health_check: typing.Optional[typing.Union[_aws_cdk_aws_ecs_ceddda9d.HealthCheck, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__60923688f982908f977f559dbd1295485a3b0547df3c45291a862130dede0c3e(
    value: _aws_cdk_aws_iam_ceddda9d.Role,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0e1edfc306738ea99e0bd03a55876d7f75a063970dd3103fc1bbb766dff014b1(
    *,
    certificate_arn: builtins.str,
    cluster: _aws_cdk_aws_ecs_ceddda9d.ICluster,
    container_port: jsii.Number,
    environment: builtins.str,
    image_uri: builtins.str,
    service_name: builtins.str,
    vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
    auto_scaling: typing.Optional[typing.Union[AutoScalingProps, typing.Dict[builtins.str, typing.Any]]] = None,
    enable_public_load_balancer: typing.Optional[builtins.bool] = None,
    health_check: typing.Optional[typing.Union[_aws_cdk_aws_ecs_ceddda9d.HealthCheck, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__448d9aeeae459df879203fad12fb34ff1b12039929f0a465891bedcfc130f38c(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    api_gateway_props: typing.Any = None,
    create_usage_plan: typing.Optional[builtins.bool] = None,
    custom_domain_name: typing.Optional[builtins.str] = None,
    existing_lambda_obj: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.Function] = None,
    hosted_zone: typing.Optional[_aws_cdk_aws_route53_ceddda9d.IHostedZone] = None,
    lambda_function_props: typing.Optional[typing.Union[_aws_cdk_aws_lambda_ceddda9d.FunctionProps, typing.Dict[builtins.str, typing.Any]]] = None,
    log_group_props: typing.Optional[typing.Union[_aws_cdk_aws_logs_ceddda9d.LogGroupProps, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__109c686be15dfacf97f31b8340ac53463b8369382aaf60b63405ca329516af4d(
    *,
    api_gateway_props: typing.Any = None,
    create_usage_plan: typing.Optional[builtins.bool] = None,
    custom_domain_name: typing.Optional[builtins.str] = None,
    existing_lambda_obj: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.Function] = None,
    hosted_zone: typing.Optional[_aws_cdk_aws_route53_ceddda9d.IHostedZone] = None,
    lambda_function_props: typing.Optional[typing.Union[_aws_cdk_aws_lambda_ceddda9d.FunctionProps, typing.Dict[builtins.str, typing.Any]]] = None,
    log_group_props: typing.Optional[typing.Union[_aws_cdk_aws_logs_ceddda9d.LogGroupProps, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass
