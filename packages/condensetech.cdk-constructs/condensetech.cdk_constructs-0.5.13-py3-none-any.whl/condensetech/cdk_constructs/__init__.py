r'''
# Condense's CDK Constructs

This library contains constructs and stacks we use across our projects.

## Setup

<details>
  <summary>Node.js</summary>
  Install the package:

```bash
npm install @condensetech/cdk-constructs # or
yarn add @condensetech/cdk-constructs # or
pnpm add @condensetech/cdk-constructs
```

Import it:

```python
import * as condense from '@condensetech/cdk-constructs';
```

</details>
<details>
  <summary>Python</summary>
  Install the package:

```bash
pip install condensetech.cdk-constructs
```

Import it:

```py
from condensetech import cdk_constructs
```

</details>
<details>
  <summary>.NET</summary>
  Install the package:

```bash
dotnet add package CondenseTech.CdkConstructs
```

Import it:

```csharp
using CondenseTech.CdkConstructs;
```

</details>
<details>
  <summary>Go</summary>
  Install the package:

```bash
go get github.com/condensetech/cdk-constructs
```

Import it:

```go
import "github.com/condensetech/cdk-constructs"
```

</details>

## Usage

All API docs can be found in the [API.md](./API.md).

### Composable Infrastructure Constructs and Stacks

Readability and maintainability are key factors when writing IaC. By defining some high level interfaces, we can easily write constructs which don't need to be tied to the specific implementation of a resource.

For example, the [INetworking](lib/interfaces.ts), defines some high level methods to interact with a VPC. Often a VPC contains a bastion host, which should be whitelisted to databases, so the interface has a `bastionHost` property which can return the bastion host. This allows to write code like the following:

```python
interface MyDatabaseStackProps extends cdk.StackProps {
  networking: INetworking;
}
class MyDatabaseStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props: MyDatabaseStackProps) {
    super(scope, id, props);

    const db = new rds.DatabaseInstance(this, 'Database', {
      vpc: props.networking.vpc,
      ...
    });
    if (props.networking.bastionHost) {
      db.connections.allowDefaultPortFrom(props.networking.bastionHost);
    }
  }
}
```

If a certain point we want to add a bastion host, we just need to flip one single switch in the networking props, to have the bastion host able to connect to all the resources in the VPC.

Constructs and Stacks in this area:

* [Networking](lib/constructs/networking.ts) and [NetworkingStack](lib/stacks/networking.ts)
* [Aurora Cluster](lib/constructs/aurora-cluster.ts) and [AuroraClusterStack](lib/stacks/aurora-cluster.ts)
* [RDS Instance](lib/constructs/database-instance.ts) and [DatabaseInstanceStack](lib/stacks/database-instance.ts)

### Entrypoint

A typical scenario is to have one single Application Load Balancer in a VPC, which routes traffic to different services. The [Entrypoint Construct](lib/constructs/entrypoint.ts) and the [Entrypoint Stack](lib/stacks/entrypoint-stack.ts) allow to easily define this entrypoint load balancer.

The [Entrypoint#allocateListenerRule](API.md#@condensetech/cdk-constructs.Entrypoint.allocateListenerRule) method tracks in a DynamoDB table the priority of the listener rules that are being created and generates a unique priority if one is not provided. This allows to operate in scenarios where different stacks are creating listener rules for the same load balancer.

### Cloudwatch Alarms Topic

The [CloudwatchAlarmsTopicStack](lib/stacks/cloudwatch-alarms-topic-stack.ts) creates an SNS Topic which can be used as a target for Cloudwatch Alarms. In addition to link the topic to HTTPS endpoints, it can also create a Lambda function which can be used to send messages to Discord or Slack.

### Naive BasicAuth Cloudfront Function

[NaiveBasicAuthCloudfrontFunction](lib/constructs/naive-basic-auth-cloudfront-function.ts) is useful when a basic protection layer must be added to Cloudfront (for SPAs or static sites) and you just need to avoid crawlers and unwanted visitors.

### Monitoring

By instantiating a [MonitoringFacade](lib/constructs/monitoring/monitoring-facade.ts) in your stack, you can easily add monitoring to your resources. The facade will create a Cloudwatch Dashboard, and will add alarms to the resources you want to monitor.
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

import aws_cdk as _aws_cdk_ceddda9d
import aws_cdk.aws_certificatemanager as _aws_cdk_aws_certificatemanager_ceddda9d
import aws_cdk.aws_cloudfront as _aws_cdk_aws_cloudfront_ceddda9d
import aws_cdk.aws_cloudwatch as _aws_cdk_aws_cloudwatch_ceddda9d
import aws_cdk.aws_ec2 as _aws_cdk_aws_ec2_ceddda9d
import aws_cdk.aws_ecs as _aws_cdk_aws_ecs_ceddda9d
import aws_cdk.aws_elasticache as _aws_cdk_aws_elasticache_ceddda9d
import aws_cdk.aws_elasticloadbalancingv2 as _aws_cdk_aws_elasticloadbalancingv2_ceddda9d
import aws_cdk.aws_logs as _aws_cdk_aws_logs_ceddda9d
import aws_cdk.aws_rds as _aws_cdk_aws_rds_ceddda9d
import aws_cdk.aws_route53 as _aws_cdk_aws_route53_ceddda9d
import aws_cdk.aws_s3 as _aws_cdk_aws_s3_ceddda9d
import aws_cdk.aws_secretsmanager as _aws_cdk_aws_secretsmanager_ceddda9d
import aws_cdk.aws_sns as _aws_cdk_aws_sns_ceddda9d
import constructs as _constructs_77d1e7e8


@jsii.data_type(
    jsii_type="@condensetech/cdk-constructs.AlarmDefinitionProps",
    jsii_struct_bases=[],
    name_mapping={
        "alarm_id": "alarmId",
        "evaluation_periods": "evaluationPeriods",
        "metric": "metric",
        "alarm_description": "alarmDescription",
        "alarm_name": "alarmName",
        "comparison_operator": "comparisonOperator",
        "threshold": "threshold",
    },
)
class AlarmDefinitionProps:
    def __init__(
        self,
        *,
        alarm_id: builtins.str,
        evaluation_periods: jsii.Number,
        metric: _aws_cdk_aws_cloudwatch_ceddda9d.IMetric,
        alarm_description: typing.Optional[builtins.str] = None,
        alarm_name: typing.Optional[builtins.str] = None,
        comparison_operator: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.ComparisonOperator] = None,
        threshold: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param alarm_id: 
        :param evaluation_periods: 
        :param metric: 
        :param alarm_description: 
        :param alarm_name: 
        :param comparison_operator: 
        :param threshold: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bd29f942ebe15d309286d39cadd5834bfefc30f944e9e7b2839e6cc6464e645a)
            check_type(argname="argument alarm_id", value=alarm_id, expected_type=type_hints["alarm_id"])
            check_type(argname="argument evaluation_periods", value=evaluation_periods, expected_type=type_hints["evaluation_periods"])
            check_type(argname="argument metric", value=metric, expected_type=type_hints["metric"])
            check_type(argname="argument alarm_description", value=alarm_description, expected_type=type_hints["alarm_description"])
            check_type(argname="argument alarm_name", value=alarm_name, expected_type=type_hints["alarm_name"])
            check_type(argname="argument comparison_operator", value=comparison_operator, expected_type=type_hints["comparison_operator"])
            check_type(argname="argument threshold", value=threshold, expected_type=type_hints["threshold"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "alarm_id": alarm_id,
            "evaluation_periods": evaluation_periods,
            "metric": metric,
        }
        if alarm_description is not None:
            self._values["alarm_description"] = alarm_description
        if alarm_name is not None:
            self._values["alarm_name"] = alarm_name
        if comparison_operator is not None:
            self._values["comparison_operator"] = comparison_operator
        if threshold is not None:
            self._values["threshold"] = threshold

    @builtins.property
    def alarm_id(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("alarm_id")
        assert result is not None, "Required property 'alarm_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def evaluation_periods(self) -> jsii.Number:
        '''
        :stability: experimental
        '''
        result = self._values.get("evaluation_periods")
        assert result is not None, "Required property 'evaluation_periods' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def metric(self) -> _aws_cdk_aws_cloudwatch_ceddda9d.IMetric:
        '''
        :stability: experimental
        '''
        result = self._values.get("metric")
        assert result is not None, "Required property 'metric' is missing"
        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.IMetric, result)

    @builtins.property
    def alarm_description(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("alarm_description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def alarm_name(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("alarm_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def comparison_operator(
        self,
    ) -> typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.ComparisonOperator]:
        '''
        :stability: experimental
        '''
        result = self._values.get("comparison_operator")
        return typing.cast(typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.ComparisonOperator], result)

    @builtins.property
    def threshold(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("threshold")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AlarmDefinitionProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@condensetech/cdk-constructs.AllocateApplicationListenerRuleProps",
    jsii_struct_bases=[],
    name_mapping={
        "action": "action",
        "conditions": "conditions",
        "priority": "priority",
        "target_groups": "targetGroups",
    },
)
class AllocateApplicationListenerRuleProps:
    def __init__(
        self,
        *,
        action: typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ListenerAction] = None,
        conditions: typing.Optional[typing.Sequence[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ListenerCondition]] = None,
        priority: typing.Optional[jsii.Number] = None,
        target_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.IApplicationTargetGroup]] = None,
    ) -> None:
        '''(experimental) Properties for the ApplicationListenerRule.

        :param action: (experimental) Action to perform when requests are received. Only one of ``action``, ``fixedResponse``, ``redirectResponse`` or ``targetGroups`` can be specified. Default: - No action
        :param conditions: (experimental) Rule applies if matches the conditions. Default: - No conditions.
        :param priority: (experimental) Priority of the rule. The rule with the lowest priority will be used for every request. Default: - The rule will be assigned a priority automatically.
        :param target_groups: (experimental) Target groups to forward requests to. Only one of ``action``, ``fixedResponse``, ``redirectResponse`` or ``targetGroups`` can be specified. Implies a ``forward`` action. Default: - No target groups.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0436f7c6595cbd4773aabafb215f9f41c093aca919f108eb93805872a6bbd29d)
            check_type(argname="argument action", value=action, expected_type=type_hints["action"])
            check_type(argname="argument conditions", value=conditions, expected_type=type_hints["conditions"])
            check_type(argname="argument priority", value=priority, expected_type=type_hints["priority"])
            check_type(argname="argument target_groups", value=target_groups, expected_type=type_hints["target_groups"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if action is not None:
            self._values["action"] = action
        if conditions is not None:
            self._values["conditions"] = conditions
        if priority is not None:
            self._values["priority"] = priority
        if target_groups is not None:
            self._values["target_groups"] = target_groups

    @builtins.property
    def action(
        self,
    ) -> typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ListenerAction]:
        '''(experimental) Action to perform when requests are received.

        Only one of ``action``, ``fixedResponse``, ``redirectResponse`` or ``targetGroups`` can be specified.

        :default: - No action

        :stability: experimental
        '''
        result = self._values.get("action")
        return typing.cast(typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ListenerAction], result)

    @builtins.property
    def conditions(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ListenerCondition]]:
        '''(experimental) Rule applies if matches the conditions.

        :default: - No conditions.

        :see: https://docs.aws.amazon.com/elasticloadbalancing/latest/application/load-balancer-listeners.html
        :stability: experimental
        '''
        result = self._values.get("conditions")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ListenerCondition]], result)

    @builtins.property
    def priority(self) -> typing.Optional[jsii.Number]:
        '''(experimental) Priority of the rule.

        The rule with the lowest priority will be used for every request.

        :default: - The rule will be assigned a priority automatically.

        :stability: experimental
        '''
        result = self._values.get("priority")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def target_groups(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.IApplicationTargetGroup]]:
        '''(experimental) Target groups to forward requests to.

        Only one of ``action``, ``fixedResponse``, ``redirectResponse`` or ``targetGroups`` can be specified.

        Implies a ``forward`` action.

        :default: - No target groups.

        :stability: experimental
        '''
        result = self._values.get("target_groups")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.IApplicationTargetGroup]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AllocateApplicationListenerRuleProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@condensetech/cdk-constructs.AllocatePriorityProps",
    jsii_struct_bases=[],
    name_mapping={"priority": "priority"},
)
class AllocatePriorityProps:
    def __init__(self, *, priority: typing.Optional[jsii.Number] = None) -> None:
        '''(experimental) Properties for allocating a priority to an application listener rule.

        :param priority: (experimental) The priority to allocate. Default: a priority will be allocated automatically.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c53d1caad2b9718c58a4ee40428ad65e3e22af09293bdb3bee44acc69f4c2f35)
            check_type(argname="argument priority", value=priority, expected_type=type_hints["priority"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if priority is not None:
            self._values["priority"] = priority

    @builtins.property
    def priority(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The priority to allocate.

        :default: a priority will be allocated automatically.

        :stability: experimental
        '''
        result = self._values.get("priority")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AllocatePriorityProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@condensetech/cdk-constructs.ApplicationListenerPriorityAllocatorConfig",
    jsii_struct_bases=[],
    name_mapping={
        "priority_initial_value": "priorityInitialValue",
        "removal_policy": "removalPolicy",
    },
)
class ApplicationListenerPriorityAllocatorConfig:
    def __init__(
        self,
        *,
        priority_initial_value: typing.Optional[jsii.Number] = None,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    ) -> None:
        '''(experimental) Overridden config for the ApplicationListenerPriorityAllocator construct.

        :param priority_initial_value: (experimental) The initial priority value to start from. Default: 1
        :param removal_policy: (experimental) The removal policy to apply to the DynamoDB table. Default: - ``RemovalPolicy.DESTROY``

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2ccd5b51a71d2e347bc905ad6ca161e0d2a386f4c98e236c23898f3dc5ee8ebe)
            check_type(argname="argument priority_initial_value", value=priority_initial_value, expected_type=type_hints["priority_initial_value"])
            check_type(argname="argument removal_policy", value=removal_policy, expected_type=type_hints["removal_policy"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if priority_initial_value is not None:
            self._values["priority_initial_value"] = priority_initial_value
        if removal_policy is not None:
            self._values["removal_policy"] = removal_policy

    @builtins.property
    def priority_initial_value(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The initial priority value to start from.

        :default: 1

        :stability: experimental
        '''
        result = self._values.get("priority_initial_value")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def removal_policy(self) -> typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy]:
        '''(experimental) The removal policy to apply to the DynamoDB table.

        :default: - ``RemovalPolicy.DESTROY``

        :stability: experimental
        '''
        result = self._values.get("removal_policy")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ApplicationListenerPriorityAllocatorConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@condensetech/cdk-constructs.ApplicationListenerPriorityAllocatorProps",
    jsii_struct_bases=[ApplicationListenerPriorityAllocatorConfig],
    name_mapping={
        "priority_initial_value": "priorityInitialValue",
        "removal_policy": "removalPolicy",
        "listener": "listener",
        "priority_allocator_name": "priorityAllocatorName",
    },
)
class ApplicationListenerPriorityAllocatorProps(
    ApplicationListenerPriorityAllocatorConfig,
):
    def __init__(
        self,
        *,
        priority_initial_value: typing.Optional[jsii.Number] = None,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
        listener: _aws_cdk_aws_elasticloadbalancingv2_ceddda9d.IApplicationListener,
        priority_allocator_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Properties for the ApplicationListenerPriorityAllocator construct.

        :param priority_initial_value: (experimental) The initial priority value to start from. Default: 1
        :param removal_policy: (experimental) The removal policy to apply to the DynamoDB table. Default: - ``RemovalPolicy.DESTROY``
        :param listener: (experimental) Application Load Balancer Listener to allocate priorities for.
        :param priority_allocator_name: (experimental) Priority Allocator name. Default: Generated by the listener unique name.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5f8f953c716556d30741778903d495459a7f78be63d2a85ee17f15f7a6085ab1)
            check_type(argname="argument priority_initial_value", value=priority_initial_value, expected_type=type_hints["priority_initial_value"])
            check_type(argname="argument removal_policy", value=removal_policy, expected_type=type_hints["removal_policy"])
            check_type(argname="argument listener", value=listener, expected_type=type_hints["listener"])
            check_type(argname="argument priority_allocator_name", value=priority_allocator_name, expected_type=type_hints["priority_allocator_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "listener": listener,
        }
        if priority_initial_value is not None:
            self._values["priority_initial_value"] = priority_initial_value
        if removal_policy is not None:
            self._values["removal_policy"] = removal_policy
        if priority_allocator_name is not None:
            self._values["priority_allocator_name"] = priority_allocator_name

    @builtins.property
    def priority_initial_value(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The initial priority value to start from.

        :default: 1

        :stability: experimental
        '''
        result = self._values.get("priority_initial_value")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def removal_policy(self) -> typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy]:
        '''(experimental) The removal policy to apply to the DynamoDB table.

        :default: - ``RemovalPolicy.DESTROY``

        :stability: experimental
        '''
        result = self._values.get("removal_policy")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy], result)

    @builtins.property
    def listener(
        self,
    ) -> _aws_cdk_aws_elasticloadbalancingv2_ceddda9d.IApplicationListener:
        '''(experimental) Application Load Balancer Listener to allocate priorities for.

        :stability: experimental
        '''
        result = self._values.get("listener")
        assert result is not None, "Required property 'listener' is missing"
        return typing.cast(_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.IApplicationListener, result)

    @builtins.property
    def priority_allocator_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) Priority Allocator name.

        :default: Generated by the listener unique name.

        :stability: experimental
        '''
        result = self._values.get("priority_allocator_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ApplicationListenerPriorityAllocatorProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(_aws_cdk_ceddda9d.IAspect)
class ApplicationLoadBalancerMonitoringAspect(
    metaclass=jsii.JSIIMeta,
    jsii_type="@condensetech/cdk-constructs.ApplicationLoadBalancerMonitoringAspect",
):
    '''(experimental) The ApplicationLoadBalancerMonitoringAspect iterates over the Application Load Balancers and adds monitoring widgets and alarms.

    :stability: experimental
    '''

    def __init__(self, monitoring_facade: "ICondenseMonitoringFacade") -> None:
        '''
        :param monitoring_facade: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__21c7d9d40cf1792a68c47202afcaf8e6c3fdb61ac00ad196a604414b9783713c)
            check_type(argname="argument monitoring_facade", value=monitoring_facade, expected_type=type_hints["monitoring_facade"])
        jsii.create(self.__class__, self, [monitoring_facade])

    @jsii.member(jsii_name="overrideConfig")
    def override_config(
        self,
        node: _aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ApplicationLoadBalancer,
        *,
        redirect_url_limit_exceeded_threshold: typing.Optional[jsii.Number] = None,
        rejected_connections_threshold: typing.Optional[jsii.Number] = None,
        response_time_threshold: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        target5xx_errors_threshold: typing.Optional[jsii.Number] = None,
        target_connection_errors_threshold: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''(experimental) Overrides the default configuration for a specific Application Load Balancer.

        :param node: The Application Load Balancer to monitor.
        :param redirect_url_limit_exceeded_threshold: (experimental) The Redirect URL Limit Exceeded threshold. Default: 0
        :param rejected_connections_threshold: (experimental) The Rejected Connections threshold. Default: 0
        :param response_time_threshold: (experimental) The Response Time threshold. Default: - No threshold.
        :param target5xx_errors_threshold: (experimental) The 5xx Errors threshold. Default: 0
        :param target_connection_errors_threshold: (experimental) The Target Connection Errors threshold. Default: 0

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1cfa6dfa414bbd2287d047457d1e08f1c4f343fe957a79584fa8db8884bab20d)
            check_type(argname="argument node", value=node, expected_type=type_hints["node"])
        config = ApplicationLoadBalancerMonitoringConfig(
            redirect_url_limit_exceeded_threshold=redirect_url_limit_exceeded_threshold,
            rejected_connections_threshold=rejected_connections_threshold,
            response_time_threshold=response_time_threshold,
            target5xx_errors_threshold=target5xx_errors_threshold,
            target_connection_errors_threshold=target_connection_errors_threshold,
        )

        return typing.cast(None, jsii.invoke(self, "overrideConfig", [node, config]))

    @jsii.member(jsii_name="visit")
    def visit(self, node: _constructs_77d1e7e8.IConstruct) -> None:
        '''(experimental) All aspects can visit an IConstruct.

        :param node: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a315fe0f4105c7a383fb140d4165db45a3067371dbf51d7eb6f3fe7bd8166048)
            check_type(argname="argument node", value=node, expected_type=type_hints["node"])
        return typing.cast(None, jsii.invoke(self, "visit", [node]))


@jsii.data_type(
    jsii_type="@condensetech/cdk-constructs.ApplicationLoadBalancerMonitoringConfig",
    jsii_struct_bases=[],
    name_mapping={
        "redirect_url_limit_exceeded_threshold": "redirectUrlLimitExceededThreshold",
        "rejected_connections_threshold": "rejectedConnectionsThreshold",
        "response_time_threshold": "responseTimeThreshold",
        "target5xx_errors_threshold": "target5xxErrorsThreshold",
        "target_connection_errors_threshold": "targetConnectionErrorsThreshold",
    },
)
class ApplicationLoadBalancerMonitoringConfig:
    def __init__(
        self,
        *,
        redirect_url_limit_exceeded_threshold: typing.Optional[jsii.Number] = None,
        rejected_connections_threshold: typing.Optional[jsii.Number] = None,
        response_time_threshold: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        target5xx_errors_threshold: typing.Optional[jsii.Number] = None,
        target_connection_errors_threshold: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''(experimental) The ApplicationLoadBalancerMonitoringConfig defines the thresholds for the Application Load Balancer monitoring.

        :param redirect_url_limit_exceeded_threshold: (experimental) The Redirect URL Limit Exceeded threshold. Default: 0
        :param rejected_connections_threshold: (experimental) The Rejected Connections threshold. Default: 0
        :param response_time_threshold: (experimental) The Response Time threshold. Default: - No threshold.
        :param target5xx_errors_threshold: (experimental) The 5xx Errors threshold. Default: 0
        :param target_connection_errors_threshold: (experimental) The Target Connection Errors threshold. Default: 0

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cea2a4cc207c22c7090a74b53d8a6cbf6a69051c06e1e404fb043435049a4a1a)
            check_type(argname="argument redirect_url_limit_exceeded_threshold", value=redirect_url_limit_exceeded_threshold, expected_type=type_hints["redirect_url_limit_exceeded_threshold"])
            check_type(argname="argument rejected_connections_threshold", value=rejected_connections_threshold, expected_type=type_hints["rejected_connections_threshold"])
            check_type(argname="argument response_time_threshold", value=response_time_threshold, expected_type=type_hints["response_time_threshold"])
            check_type(argname="argument target5xx_errors_threshold", value=target5xx_errors_threshold, expected_type=type_hints["target5xx_errors_threshold"])
            check_type(argname="argument target_connection_errors_threshold", value=target_connection_errors_threshold, expected_type=type_hints["target_connection_errors_threshold"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if redirect_url_limit_exceeded_threshold is not None:
            self._values["redirect_url_limit_exceeded_threshold"] = redirect_url_limit_exceeded_threshold
        if rejected_connections_threshold is not None:
            self._values["rejected_connections_threshold"] = rejected_connections_threshold
        if response_time_threshold is not None:
            self._values["response_time_threshold"] = response_time_threshold
        if target5xx_errors_threshold is not None:
            self._values["target5xx_errors_threshold"] = target5xx_errors_threshold
        if target_connection_errors_threshold is not None:
            self._values["target_connection_errors_threshold"] = target_connection_errors_threshold

    @builtins.property
    def redirect_url_limit_exceeded_threshold(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The Redirect URL Limit Exceeded threshold.

        :default: 0

        :stability: experimental
        '''
        result = self._values.get("redirect_url_limit_exceeded_threshold")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def rejected_connections_threshold(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The Rejected Connections threshold.

        :default: 0

        :stability: experimental
        '''
        result = self._values.get("rejected_connections_threshold")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def response_time_threshold(self) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        '''(experimental) The Response Time threshold.

        :default: - No threshold.

        :stability: experimental
        '''
        result = self._values.get("response_time_threshold")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], result)

    @builtins.property
    def target5xx_errors_threshold(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The 5xx Errors threshold.

        :default: 0

        :stability: experimental
        '''
        result = self._values.get("target5xx_errors_threshold")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def target_connection_errors_threshold(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The Target Connection Errors threshold.

        :default: 0

        :stability: experimental
        '''
        result = self._values.get("target_connection_errors_threshold")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ApplicationLoadBalancerMonitoringConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@condensetech/cdk-constructs.AuroraClusterProps",
    jsii_struct_bases=[],
    name_mapping={
        "engine": "engine",
        "networking": "networking",
        "backup_retention": "backupRetention",
        "cloudwatch_logs_exports": "cloudwatchLogsExports",
        "cloudwatch_logs_retention": "cloudwatchLogsRetention",
        "cluster_identifier": "clusterIdentifier",
        "cluster_parameters": "clusterParameters",
        "credentials_secret_name": "credentialsSecretName",
        "credentials_username": "credentialsUsername",
        "database_name": "databaseName",
        "instance_parameters": "instanceParameters",
        "parameters": "parameters",
        "readers": "readers",
        "removal_policy": "removalPolicy",
        "security_group_name": "securityGroupName",
        "writer": "writer",
    },
)
class AuroraClusterProps:
    def __init__(
        self,
        *,
        engine: _aws_cdk_aws_rds_ceddda9d.IClusterEngine,
        networking: "INetworking",
        backup_retention: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        cloudwatch_logs_exports: typing.Optional[typing.Sequence[builtins.str]] = None,
        cloudwatch_logs_retention: typing.Optional[_aws_cdk_aws_logs_ceddda9d.RetentionDays] = None,
        cluster_identifier: typing.Optional[builtins.str] = None,
        cluster_parameters: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        credentials_secret_name: typing.Optional[builtins.str] = None,
        credentials_username: typing.Optional[builtins.str] = None,
        database_name: typing.Optional[builtins.str] = None,
        instance_parameters: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        parameters: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        readers: typing.Optional[typing.Sequence[_aws_cdk_aws_rds_ceddda9d.IClusterInstance]] = None,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
        security_group_name: typing.Optional[builtins.str] = None,
        writer: typing.Optional[_aws_cdk_aws_rds_ceddda9d.IClusterInstance] = None,
    ) -> None:
        '''(experimental) Properties for the AuroraCluster construct.

        :param engine: (experimental) The engine of the Aurora cluster.
        :param networking: (experimental) The networking configuration for the Aurora cluster.
        :param backup_retention: (experimental) The backup retention period. Default: - It uses the default applied by `rds.DatabaseClusterProps#backup <https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_rds.DatabaseClusterProps.html#backup>`_.
        :param cloudwatch_logs_exports: (experimental) The list of log types that need to be enabled for exporting to CloudWatch Logs. Default: - No log types are enabled.
        :param cloudwatch_logs_retention: (experimental) The number of days log events are kept in CloudWatch Logs. When updating this property, unsetting it doesn't remove the log retention policy. To remove the retention policy, set the value to Infinity. Default: logs never expire
        :param cluster_identifier: (experimental) The identifier of the cluster. If not specified, it relies on the underlying default naming.
        :param cluster_parameters: (experimental) The parameters to override in the cluster parameter group. Default: - No parameter is overridden.
        :param credentials_secret_name: (experimental) The name of the secret that stores the credentials of the database. Default: ``${construct.node.path}/secret``
        :param credentials_username: (experimental) The username of the database. Default: db_user
        :param database_name: (experimental) The name of the database. Default: - No default database is created.
        :param instance_parameters: (experimental) The parameters to override in the instance parameter group. Default: - No parameter is overridden.
        :param parameters: (experimental) The parameters to override in all of the parameter groups. Default: - No parameter is overridden.
        :param readers: (experimental) The reader instances of the Aurora cluster. Default: - No reader instances are created.
        :param removal_policy: (experimental) The removal policy to apply when the cluster is removed. Default: RemovalPolicy.RETAIN
        :param security_group_name: (experimental) The name of the security group. Default: - ``${construct.node.path}-sg``.
        :param writer: (experimental) The writer instance of the Aurora cluster. Default: - A provisioned instance with the minimum instance type based on the engine type.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e574b5d10e1d847dabe15ebbbc4935b04c4f2cbd8a36b95cdb4526ea5fbf9956)
            check_type(argname="argument engine", value=engine, expected_type=type_hints["engine"])
            check_type(argname="argument networking", value=networking, expected_type=type_hints["networking"])
            check_type(argname="argument backup_retention", value=backup_retention, expected_type=type_hints["backup_retention"])
            check_type(argname="argument cloudwatch_logs_exports", value=cloudwatch_logs_exports, expected_type=type_hints["cloudwatch_logs_exports"])
            check_type(argname="argument cloudwatch_logs_retention", value=cloudwatch_logs_retention, expected_type=type_hints["cloudwatch_logs_retention"])
            check_type(argname="argument cluster_identifier", value=cluster_identifier, expected_type=type_hints["cluster_identifier"])
            check_type(argname="argument cluster_parameters", value=cluster_parameters, expected_type=type_hints["cluster_parameters"])
            check_type(argname="argument credentials_secret_name", value=credentials_secret_name, expected_type=type_hints["credentials_secret_name"])
            check_type(argname="argument credentials_username", value=credentials_username, expected_type=type_hints["credentials_username"])
            check_type(argname="argument database_name", value=database_name, expected_type=type_hints["database_name"])
            check_type(argname="argument instance_parameters", value=instance_parameters, expected_type=type_hints["instance_parameters"])
            check_type(argname="argument parameters", value=parameters, expected_type=type_hints["parameters"])
            check_type(argname="argument readers", value=readers, expected_type=type_hints["readers"])
            check_type(argname="argument removal_policy", value=removal_policy, expected_type=type_hints["removal_policy"])
            check_type(argname="argument security_group_name", value=security_group_name, expected_type=type_hints["security_group_name"])
            check_type(argname="argument writer", value=writer, expected_type=type_hints["writer"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "engine": engine,
            "networking": networking,
        }
        if backup_retention is not None:
            self._values["backup_retention"] = backup_retention
        if cloudwatch_logs_exports is not None:
            self._values["cloudwatch_logs_exports"] = cloudwatch_logs_exports
        if cloudwatch_logs_retention is not None:
            self._values["cloudwatch_logs_retention"] = cloudwatch_logs_retention
        if cluster_identifier is not None:
            self._values["cluster_identifier"] = cluster_identifier
        if cluster_parameters is not None:
            self._values["cluster_parameters"] = cluster_parameters
        if credentials_secret_name is not None:
            self._values["credentials_secret_name"] = credentials_secret_name
        if credentials_username is not None:
            self._values["credentials_username"] = credentials_username
        if database_name is not None:
            self._values["database_name"] = database_name
        if instance_parameters is not None:
            self._values["instance_parameters"] = instance_parameters
        if parameters is not None:
            self._values["parameters"] = parameters
        if readers is not None:
            self._values["readers"] = readers
        if removal_policy is not None:
            self._values["removal_policy"] = removal_policy
        if security_group_name is not None:
            self._values["security_group_name"] = security_group_name
        if writer is not None:
            self._values["writer"] = writer

    @builtins.property
    def engine(self) -> _aws_cdk_aws_rds_ceddda9d.IClusterEngine:
        '''(experimental) The engine of the Aurora cluster.

        :stability: experimental
        '''
        result = self._values.get("engine")
        assert result is not None, "Required property 'engine' is missing"
        return typing.cast(_aws_cdk_aws_rds_ceddda9d.IClusterEngine, result)

    @builtins.property
    def networking(self) -> "INetworking":
        '''(experimental) The networking configuration for the Aurora cluster.

        :stability: experimental
        '''
        result = self._values.get("networking")
        assert result is not None, "Required property 'networking' is missing"
        return typing.cast("INetworking", result)

    @builtins.property
    def backup_retention(self) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        '''(experimental) The backup retention period.

        :default: - It uses the default applied by `rds.DatabaseClusterProps#backup <https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_rds.DatabaseClusterProps.html#backup>`_.

        :stability: experimental
        '''
        result = self._values.get("backup_retention")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], result)

    @builtins.property
    def cloudwatch_logs_exports(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) The list of log types that need to be enabled for exporting to CloudWatch Logs.

        :default: - No log types are enabled.

        :stability: experimental
        '''
        result = self._values.get("cloudwatch_logs_exports")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def cloudwatch_logs_retention(
        self,
    ) -> typing.Optional[_aws_cdk_aws_logs_ceddda9d.RetentionDays]:
        '''(experimental) The number of days log events are kept in CloudWatch Logs.

        When updating this property, unsetting it doesn't remove the log retention policy. To remove the retention policy, set the value to Infinity.

        :default: logs never expire

        :stability: experimental
        '''
        result = self._values.get("cloudwatch_logs_retention")
        return typing.cast(typing.Optional[_aws_cdk_aws_logs_ceddda9d.RetentionDays], result)

    @builtins.property
    def cluster_identifier(self) -> typing.Optional[builtins.str]:
        '''(experimental) The identifier of the cluster.

        If not specified, it relies on the underlying default naming.

        :stability: experimental
        '''
        result = self._values.get("cluster_identifier")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def cluster_parameters(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''(experimental) The parameters to override in the cluster parameter group.

        :default: - No parameter is overridden.

        :stability: experimental
        '''
        result = self._values.get("cluster_parameters")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def credentials_secret_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of the secret that stores the credentials of the database.

        :default: ``${construct.node.path}/secret``

        :stability: experimental
        '''
        result = self._values.get("credentials_secret_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def credentials_username(self) -> typing.Optional[builtins.str]:
        '''(experimental) The username of the database.

        :default: db_user

        :stability: experimental
        '''
        result = self._values.get("credentials_username")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def database_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of the database.

        :default: - No default database is created.

        :stability: experimental
        '''
        result = self._values.get("database_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def instance_parameters(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''(experimental) The parameters to override in the instance parameter group.

        :default: - No parameter is overridden.

        :stability: experimental
        '''
        result = self._values.get("instance_parameters")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def parameters(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''(experimental) The parameters to override in all of the parameter groups.

        :default: - No parameter is overridden.

        :stability: experimental
        '''
        result = self._values.get("parameters")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def readers(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_rds_ceddda9d.IClusterInstance]]:
        '''(experimental) The reader instances of the Aurora cluster.

        :default: - No reader instances are created.

        :stability: experimental
        '''
        result = self._values.get("readers")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_rds_ceddda9d.IClusterInstance]], result)

    @builtins.property
    def removal_policy(self) -> typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy]:
        '''(experimental) The removal policy to apply when the cluster is removed.

        :default: RemovalPolicy.RETAIN

        :stability: experimental
        '''
        result = self._values.get("removal_policy")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy], result)

    @builtins.property
    def security_group_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of the security group.

        :default: - ``${construct.node.path}-sg``.

        :stability: experimental
        '''
        result = self._values.get("security_group_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def writer(self) -> typing.Optional[_aws_cdk_aws_rds_ceddda9d.IClusterInstance]:
        '''(experimental) The writer instance of the Aurora cluster.

        :default: - A provisioned instance with the minimum instance type based on the engine type.

        :stability: experimental
        '''
        result = self._values.get("writer")
        return typing.cast(typing.Optional[_aws_cdk_aws_rds_ceddda9d.IClusterInstance], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AuroraClusterProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@condensetech/cdk-constructs.AuroraClusterStackProps",
    jsii_struct_bases=[AuroraClusterProps, _aws_cdk_ceddda9d.StackProps],
    name_mapping={
        "engine": "engine",
        "networking": "networking",
        "backup_retention": "backupRetention",
        "cloudwatch_logs_exports": "cloudwatchLogsExports",
        "cloudwatch_logs_retention": "cloudwatchLogsRetention",
        "cluster_identifier": "clusterIdentifier",
        "cluster_parameters": "clusterParameters",
        "credentials_secret_name": "credentialsSecretName",
        "credentials_username": "credentialsUsername",
        "database_name": "databaseName",
        "instance_parameters": "instanceParameters",
        "parameters": "parameters",
        "readers": "readers",
        "removal_policy": "removalPolicy",
        "security_group_name": "securityGroupName",
        "writer": "writer",
        "analytics_reporting": "analyticsReporting",
        "cross_region_references": "crossRegionReferences",
        "description": "description",
        "env": "env",
        "permissions_boundary": "permissionsBoundary",
        "stack_name": "stackName",
        "suppress_template_indentation": "suppressTemplateIndentation",
        "synthesizer": "synthesizer",
        "tags": "tags",
        "termination_protection": "terminationProtection",
        "monitoring": "monitoring",
    },
)
class AuroraClusterStackProps(AuroraClusterProps, _aws_cdk_ceddda9d.StackProps):
    def __init__(
        self,
        *,
        engine: _aws_cdk_aws_rds_ceddda9d.IClusterEngine,
        networking: "INetworking",
        backup_retention: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        cloudwatch_logs_exports: typing.Optional[typing.Sequence[builtins.str]] = None,
        cloudwatch_logs_retention: typing.Optional[_aws_cdk_aws_logs_ceddda9d.RetentionDays] = None,
        cluster_identifier: typing.Optional[builtins.str] = None,
        cluster_parameters: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        credentials_secret_name: typing.Optional[builtins.str] = None,
        credentials_username: typing.Optional[builtins.str] = None,
        database_name: typing.Optional[builtins.str] = None,
        instance_parameters: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        parameters: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        readers: typing.Optional[typing.Sequence[_aws_cdk_aws_rds_ceddda9d.IClusterInstance]] = None,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
        security_group_name: typing.Optional[builtins.str] = None,
        writer: typing.Optional[_aws_cdk_aws_rds_ceddda9d.IClusterInstance] = None,
        analytics_reporting: typing.Optional[builtins.bool] = None,
        cross_region_references: typing.Optional[builtins.bool] = None,
        description: typing.Optional[builtins.str] = None,
        env: typing.Optional[typing.Union[_aws_cdk_ceddda9d.Environment, typing.Dict[builtins.str, typing.Any]]] = None,
        permissions_boundary: typing.Optional[_aws_cdk_ceddda9d.PermissionsBoundary] = None,
        stack_name: typing.Optional[builtins.str] = None,
        suppress_template_indentation: typing.Optional[builtins.bool] = None,
        synthesizer: typing.Optional[_aws_cdk_ceddda9d.IStackSynthesizer] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        termination_protection: typing.Optional[builtins.bool] = None,
        monitoring: typing.Optional[typing.Union["MonitoringFacadeProps", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''(experimental) Properties for the AuroraClusterStack.

        :param engine: (experimental) The engine of the Aurora cluster.
        :param networking: (experimental) The networking configuration for the Aurora cluster.
        :param backup_retention: (experimental) The backup retention period. Default: - It uses the default applied by `rds.DatabaseClusterProps#backup <https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_rds.DatabaseClusterProps.html#backup>`_.
        :param cloudwatch_logs_exports: (experimental) The list of log types that need to be enabled for exporting to CloudWatch Logs. Default: - No log types are enabled.
        :param cloudwatch_logs_retention: (experimental) The number of days log events are kept in CloudWatch Logs. When updating this property, unsetting it doesn't remove the log retention policy. To remove the retention policy, set the value to Infinity. Default: logs never expire
        :param cluster_identifier: (experimental) The identifier of the cluster. If not specified, it relies on the underlying default naming.
        :param cluster_parameters: (experimental) The parameters to override in the cluster parameter group. Default: - No parameter is overridden.
        :param credentials_secret_name: (experimental) The name of the secret that stores the credentials of the database. Default: ``${construct.node.path}/secret``
        :param credentials_username: (experimental) The username of the database. Default: db_user
        :param database_name: (experimental) The name of the database. Default: - No default database is created.
        :param instance_parameters: (experimental) The parameters to override in the instance parameter group. Default: - No parameter is overridden.
        :param parameters: (experimental) The parameters to override in all of the parameter groups. Default: - No parameter is overridden.
        :param readers: (experimental) The reader instances of the Aurora cluster. Default: - No reader instances are created.
        :param removal_policy: (experimental) The removal policy to apply when the cluster is removed. Default: RemovalPolicy.RETAIN
        :param security_group_name: (experimental) The name of the security group. Default: - ``${construct.node.path}-sg``.
        :param writer: (experimental) The writer instance of the Aurora cluster. Default: - A provisioned instance with the minimum instance type based on the engine type.
        :param analytics_reporting: Include runtime versioning information in this Stack. Default: ``analyticsReporting`` setting of containing ``App``, or value of 'aws:cdk:version-reporting' context key
        :param cross_region_references: Enable this flag to allow native cross region stack references. Enabling this will create a CloudFormation custom resource in both the producing stack and consuming stack in order to perform the export/import This feature is currently experimental Default: false
        :param description: A description of the stack. Default: - No description.
        :param env: The AWS environment (account/region) where this stack will be deployed. Set the ``region``/``account`` fields of ``env`` to either a concrete value to select the indicated environment (recommended for production stacks), or to the values of environment variables ``CDK_DEFAULT_REGION``/``CDK_DEFAULT_ACCOUNT`` to let the target environment depend on the AWS credentials/configuration that the CDK CLI is executed under (recommended for development stacks). If the ``Stack`` is instantiated inside a ``Stage``, any undefined ``region``/``account`` fields from ``env`` will default to the same field on the encompassing ``Stage``, if configured there. If either ``region`` or ``account`` are not set nor inherited from ``Stage``, the Stack will be considered "*environment-agnostic*"". Environment-agnostic stacks can be deployed to any environment but may not be able to take advantage of all features of the CDK. For example, they will not be able to use environmental context lookups such as ``ec2.Vpc.fromLookup`` and will not automatically translate Service Principals to the right format based on the environment's AWS partition, and other such enhancements. Default: - The environment of the containing ``Stage`` if available, otherwise create the stack will be environment-agnostic.
        :param permissions_boundary: Options for applying a permissions boundary to all IAM Roles and Users created within this Stage. Default: - no permissions boundary is applied
        :param stack_name: Name to deploy the stack with. Default: - Derived from construct path.
        :param suppress_template_indentation: Enable this flag to suppress indentation in generated CloudFormation templates. If not specified, the value of the ``@aws-cdk/core:suppressTemplateIndentation`` context key will be used. If that is not specified, then the default value ``false`` will be used. Default: - the value of ``@aws-cdk/core:suppressTemplateIndentation``, or ``false`` if that is not set.
        :param synthesizer: Synthesis method to use while deploying this stack. The Stack Synthesizer controls aspects of synthesis and deployment, like how assets are referenced and what IAM roles to use. For more information, see the README of the main CDK package. If not specified, the ``defaultStackSynthesizer`` from ``App`` will be used. If that is not specified, ``DefaultStackSynthesizer`` is used if ``@aws-cdk/core:newStyleStackSynthesis`` is set to ``true`` or the CDK major version is v2. In CDK v1 ``LegacyStackSynthesizer`` is the default if no other synthesizer is specified. Default: - The synthesizer specified on ``App``, or ``DefaultStackSynthesizer`` otherwise.
        :param tags: Stack tags that will be applied to all the taggable resources and the stack itself. Default: {}
        :param termination_protection: Whether to enable termination protection for this stack. Default: false
        :param monitoring: (experimental) The monitoring configuration to apply to this stack. Default: - No monitoring.

        :stability: experimental
        '''
        if isinstance(env, dict):
            env = _aws_cdk_ceddda9d.Environment(**env)
        if isinstance(monitoring, dict):
            monitoring = MonitoringFacadeProps(**monitoring)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d7e4ee724edadf6dd8693e56cd66d90d5cba69a05ad5791d1271729d01dabc4c)
            check_type(argname="argument engine", value=engine, expected_type=type_hints["engine"])
            check_type(argname="argument networking", value=networking, expected_type=type_hints["networking"])
            check_type(argname="argument backup_retention", value=backup_retention, expected_type=type_hints["backup_retention"])
            check_type(argname="argument cloudwatch_logs_exports", value=cloudwatch_logs_exports, expected_type=type_hints["cloudwatch_logs_exports"])
            check_type(argname="argument cloudwatch_logs_retention", value=cloudwatch_logs_retention, expected_type=type_hints["cloudwatch_logs_retention"])
            check_type(argname="argument cluster_identifier", value=cluster_identifier, expected_type=type_hints["cluster_identifier"])
            check_type(argname="argument cluster_parameters", value=cluster_parameters, expected_type=type_hints["cluster_parameters"])
            check_type(argname="argument credentials_secret_name", value=credentials_secret_name, expected_type=type_hints["credentials_secret_name"])
            check_type(argname="argument credentials_username", value=credentials_username, expected_type=type_hints["credentials_username"])
            check_type(argname="argument database_name", value=database_name, expected_type=type_hints["database_name"])
            check_type(argname="argument instance_parameters", value=instance_parameters, expected_type=type_hints["instance_parameters"])
            check_type(argname="argument parameters", value=parameters, expected_type=type_hints["parameters"])
            check_type(argname="argument readers", value=readers, expected_type=type_hints["readers"])
            check_type(argname="argument removal_policy", value=removal_policy, expected_type=type_hints["removal_policy"])
            check_type(argname="argument security_group_name", value=security_group_name, expected_type=type_hints["security_group_name"])
            check_type(argname="argument writer", value=writer, expected_type=type_hints["writer"])
            check_type(argname="argument analytics_reporting", value=analytics_reporting, expected_type=type_hints["analytics_reporting"])
            check_type(argname="argument cross_region_references", value=cross_region_references, expected_type=type_hints["cross_region_references"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument env", value=env, expected_type=type_hints["env"])
            check_type(argname="argument permissions_boundary", value=permissions_boundary, expected_type=type_hints["permissions_boundary"])
            check_type(argname="argument stack_name", value=stack_name, expected_type=type_hints["stack_name"])
            check_type(argname="argument suppress_template_indentation", value=suppress_template_indentation, expected_type=type_hints["suppress_template_indentation"])
            check_type(argname="argument synthesizer", value=synthesizer, expected_type=type_hints["synthesizer"])
            check_type(argname="argument tags", value=tags, expected_type=type_hints["tags"])
            check_type(argname="argument termination_protection", value=termination_protection, expected_type=type_hints["termination_protection"])
            check_type(argname="argument monitoring", value=monitoring, expected_type=type_hints["monitoring"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "engine": engine,
            "networking": networking,
        }
        if backup_retention is not None:
            self._values["backup_retention"] = backup_retention
        if cloudwatch_logs_exports is not None:
            self._values["cloudwatch_logs_exports"] = cloudwatch_logs_exports
        if cloudwatch_logs_retention is not None:
            self._values["cloudwatch_logs_retention"] = cloudwatch_logs_retention
        if cluster_identifier is not None:
            self._values["cluster_identifier"] = cluster_identifier
        if cluster_parameters is not None:
            self._values["cluster_parameters"] = cluster_parameters
        if credentials_secret_name is not None:
            self._values["credentials_secret_name"] = credentials_secret_name
        if credentials_username is not None:
            self._values["credentials_username"] = credentials_username
        if database_name is not None:
            self._values["database_name"] = database_name
        if instance_parameters is not None:
            self._values["instance_parameters"] = instance_parameters
        if parameters is not None:
            self._values["parameters"] = parameters
        if readers is not None:
            self._values["readers"] = readers
        if removal_policy is not None:
            self._values["removal_policy"] = removal_policy
        if security_group_name is not None:
            self._values["security_group_name"] = security_group_name
        if writer is not None:
            self._values["writer"] = writer
        if analytics_reporting is not None:
            self._values["analytics_reporting"] = analytics_reporting
        if cross_region_references is not None:
            self._values["cross_region_references"] = cross_region_references
        if description is not None:
            self._values["description"] = description
        if env is not None:
            self._values["env"] = env
        if permissions_boundary is not None:
            self._values["permissions_boundary"] = permissions_boundary
        if stack_name is not None:
            self._values["stack_name"] = stack_name
        if suppress_template_indentation is not None:
            self._values["suppress_template_indentation"] = suppress_template_indentation
        if synthesizer is not None:
            self._values["synthesizer"] = synthesizer
        if tags is not None:
            self._values["tags"] = tags
        if termination_protection is not None:
            self._values["termination_protection"] = termination_protection
        if monitoring is not None:
            self._values["monitoring"] = monitoring

    @builtins.property
    def engine(self) -> _aws_cdk_aws_rds_ceddda9d.IClusterEngine:
        '''(experimental) The engine of the Aurora cluster.

        :stability: experimental
        '''
        result = self._values.get("engine")
        assert result is not None, "Required property 'engine' is missing"
        return typing.cast(_aws_cdk_aws_rds_ceddda9d.IClusterEngine, result)

    @builtins.property
    def networking(self) -> "INetworking":
        '''(experimental) The networking configuration for the Aurora cluster.

        :stability: experimental
        '''
        result = self._values.get("networking")
        assert result is not None, "Required property 'networking' is missing"
        return typing.cast("INetworking", result)

    @builtins.property
    def backup_retention(self) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        '''(experimental) The backup retention period.

        :default: - It uses the default applied by `rds.DatabaseClusterProps#backup <https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_rds.DatabaseClusterProps.html#backup>`_.

        :stability: experimental
        '''
        result = self._values.get("backup_retention")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], result)

    @builtins.property
    def cloudwatch_logs_exports(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) The list of log types that need to be enabled for exporting to CloudWatch Logs.

        :default: - No log types are enabled.

        :stability: experimental
        '''
        result = self._values.get("cloudwatch_logs_exports")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def cloudwatch_logs_retention(
        self,
    ) -> typing.Optional[_aws_cdk_aws_logs_ceddda9d.RetentionDays]:
        '''(experimental) The number of days log events are kept in CloudWatch Logs.

        When updating this property, unsetting it doesn't remove the log retention policy. To remove the retention policy, set the value to Infinity.

        :default: logs never expire

        :stability: experimental
        '''
        result = self._values.get("cloudwatch_logs_retention")
        return typing.cast(typing.Optional[_aws_cdk_aws_logs_ceddda9d.RetentionDays], result)

    @builtins.property
    def cluster_identifier(self) -> typing.Optional[builtins.str]:
        '''(experimental) The identifier of the cluster.

        If not specified, it relies on the underlying default naming.

        :stability: experimental
        '''
        result = self._values.get("cluster_identifier")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def cluster_parameters(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''(experimental) The parameters to override in the cluster parameter group.

        :default: - No parameter is overridden.

        :stability: experimental
        '''
        result = self._values.get("cluster_parameters")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def credentials_secret_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of the secret that stores the credentials of the database.

        :default: ``${construct.node.path}/secret``

        :stability: experimental
        '''
        result = self._values.get("credentials_secret_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def credentials_username(self) -> typing.Optional[builtins.str]:
        '''(experimental) The username of the database.

        :default: db_user

        :stability: experimental
        '''
        result = self._values.get("credentials_username")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def database_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of the database.

        :default: - No default database is created.

        :stability: experimental
        '''
        result = self._values.get("database_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def instance_parameters(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''(experimental) The parameters to override in the instance parameter group.

        :default: - No parameter is overridden.

        :stability: experimental
        '''
        result = self._values.get("instance_parameters")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def parameters(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''(experimental) The parameters to override in all of the parameter groups.

        :default: - No parameter is overridden.

        :stability: experimental
        '''
        result = self._values.get("parameters")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def readers(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_rds_ceddda9d.IClusterInstance]]:
        '''(experimental) The reader instances of the Aurora cluster.

        :default: - No reader instances are created.

        :stability: experimental
        '''
        result = self._values.get("readers")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_rds_ceddda9d.IClusterInstance]], result)

    @builtins.property
    def removal_policy(self) -> typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy]:
        '''(experimental) The removal policy to apply when the cluster is removed.

        :default: RemovalPolicy.RETAIN

        :stability: experimental
        '''
        result = self._values.get("removal_policy")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy], result)

    @builtins.property
    def security_group_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of the security group.

        :default: - ``${construct.node.path}-sg``.

        :stability: experimental
        '''
        result = self._values.get("security_group_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def writer(self) -> typing.Optional[_aws_cdk_aws_rds_ceddda9d.IClusterInstance]:
        '''(experimental) The writer instance of the Aurora cluster.

        :default: - A provisioned instance with the minimum instance type based on the engine type.

        :stability: experimental
        '''
        result = self._values.get("writer")
        return typing.cast(typing.Optional[_aws_cdk_aws_rds_ceddda9d.IClusterInstance], result)

    @builtins.property
    def analytics_reporting(self) -> typing.Optional[builtins.bool]:
        '''Include runtime versioning information in this Stack.

        :default:

        ``analyticsReporting`` setting of containing ``App``, or value of
        'aws:cdk:version-reporting' context key
        '''
        result = self._values.get("analytics_reporting")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def cross_region_references(self) -> typing.Optional[builtins.bool]:
        '''Enable this flag to allow native cross region stack references.

        Enabling this will create a CloudFormation custom resource
        in both the producing stack and consuming stack in order to perform the export/import

        This feature is currently experimental

        :default: false
        '''
        result = self._values.get("cross_region_references")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''A description of the stack.

        :default: - No description.
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def env(self) -> typing.Optional[_aws_cdk_ceddda9d.Environment]:
        '''The AWS environment (account/region) where this stack will be deployed.

        Set the ``region``/``account`` fields of ``env`` to either a concrete value to
        select the indicated environment (recommended for production stacks), or to
        the values of environment variables
        ``CDK_DEFAULT_REGION``/``CDK_DEFAULT_ACCOUNT`` to let the target environment
        depend on the AWS credentials/configuration that the CDK CLI is executed
        under (recommended for development stacks).

        If the ``Stack`` is instantiated inside a ``Stage``, any undefined
        ``region``/``account`` fields from ``env`` will default to the same field on the
        encompassing ``Stage``, if configured there.

        If either ``region`` or ``account`` are not set nor inherited from ``Stage``, the
        Stack will be considered "*environment-agnostic*"". Environment-agnostic
        stacks can be deployed to any environment but may not be able to take
        advantage of all features of the CDK. For example, they will not be able to
        use environmental context lookups such as ``ec2.Vpc.fromLookup`` and will not
        automatically translate Service Principals to the right format based on the
        environment's AWS partition, and other such enhancements.

        :default:

        - The environment of the containing ``Stage`` if available,
        otherwise create the stack will be environment-agnostic.

        Example::

            // Use a concrete account and region to deploy this stack to:
            // `.account` and `.region` will simply return these values.
            new Stack(app, 'Stack1', {
              env: {
                account: '123456789012',
                region: 'us-east-1'
              },
            });
            
            // Use the CLI's current credentials to determine the target environment:
            // `.account` and `.region` will reflect the account+region the CLI
            // is configured to use (based on the user CLI credentials)
            new Stack(app, 'Stack2', {
              env: {
                account: process.env.CDK_DEFAULT_ACCOUNT,
                region: process.env.CDK_DEFAULT_REGION
              },
            });
            
            // Define multiple stacks stage associated with an environment
            const myStage = new Stage(app, 'MyStage', {
              env: {
                account: '123456789012',
                region: 'us-east-1'
              }
            });
            
            // both of these stacks will use the stage's account/region:
            // `.account` and `.region` will resolve to the concrete values as above
            new MyStack(myStage, 'Stack1');
            new YourStack(myStage, 'Stack2');
            
            // Define an environment-agnostic stack:
            // `.account` and `.region` will resolve to `{ "Ref": "AWS::AccountId" }` and `{ "Ref": "AWS::Region" }` respectively.
            // which will only resolve to actual values by CloudFormation during deployment.
            new MyStack(app, 'Stack1');
        '''
        result = self._values.get("env")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Environment], result)

    @builtins.property
    def permissions_boundary(
        self,
    ) -> typing.Optional[_aws_cdk_ceddda9d.PermissionsBoundary]:
        '''Options for applying a permissions boundary to all IAM Roles and Users created within this Stage.

        :default: - no permissions boundary is applied
        '''
        result = self._values.get("permissions_boundary")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.PermissionsBoundary], result)

    @builtins.property
    def stack_name(self) -> typing.Optional[builtins.str]:
        '''Name to deploy the stack with.

        :default: - Derived from construct path.
        '''
        result = self._values.get("stack_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def suppress_template_indentation(self) -> typing.Optional[builtins.bool]:
        '''Enable this flag to suppress indentation in generated CloudFormation templates.

        If not specified, the value of the ``@aws-cdk/core:suppressTemplateIndentation``
        context key will be used. If that is not specified, then the
        default value ``false`` will be used.

        :default: - the value of ``@aws-cdk/core:suppressTemplateIndentation``, or ``false`` if that is not set.
        '''
        result = self._values.get("suppress_template_indentation")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def synthesizer(self) -> typing.Optional[_aws_cdk_ceddda9d.IStackSynthesizer]:
        '''Synthesis method to use while deploying this stack.

        The Stack Synthesizer controls aspects of synthesis and deployment,
        like how assets are referenced and what IAM roles to use. For more
        information, see the README of the main CDK package.

        If not specified, the ``defaultStackSynthesizer`` from ``App`` will be used.
        If that is not specified, ``DefaultStackSynthesizer`` is used if
        ``@aws-cdk/core:newStyleStackSynthesis`` is set to ``true`` or the CDK major
        version is v2. In CDK v1 ``LegacyStackSynthesizer`` is the default if no
        other synthesizer is specified.

        :default: - The synthesizer specified on ``App``, or ``DefaultStackSynthesizer`` otherwise.
        '''
        result = self._values.get("synthesizer")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.IStackSynthesizer], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Stack tags that will be applied to all the taggable resources and the stack itself.

        :default: {}
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def termination_protection(self) -> typing.Optional[builtins.bool]:
        '''Whether to enable termination protection for this stack.

        :default: false
        '''
        result = self._values.get("termination_protection")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def monitoring(self) -> typing.Optional["MonitoringFacadeProps"]:
        '''(experimental) The monitoring configuration to apply to this stack.

        :default: - No monitoring.

        :stability: experimental
        '''
        result = self._values.get("monitoring")
        return typing.cast(typing.Optional["MonitoringFacadeProps"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AuroraClusterStackProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@condensetech/cdk-constructs.BuildAlarmsProps",
    jsii_struct_bases=[],
    name_mapping={
        "alarms": "alarms",
        "node": "node",
        "node_identifier": "nodeIdentifier",
    },
)
class BuildAlarmsProps:
    def __init__(
        self,
        *,
        alarms: typing.Sequence[typing.Union[AlarmDefinitionProps, typing.Dict[builtins.str, typing.Any]]],
        node: _constructs_77d1e7e8.Construct,
        node_identifier: builtins.str,
    ) -> None:
        '''
        :param alarms: 
        :param node: 
        :param node_identifier: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8bce0c670e92bd5df1aea2a72a8b2611d5c35bac73dcaba00625e9d792bd3492)
            check_type(argname="argument alarms", value=alarms, expected_type=type_hints["alarms"])
            check_type(argname="argument node", value=node, expected_type=type_hints["node"])
            check_type(argname="argument node_identifier", value=node_identifier, expected_type=type_hints["node_identifier"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "alarms": alarms,
            "node": node,
            "node_identifier": node_identifier,
        }

    @builtins.property
    def alarms(self) -> typing.List[AlarmDefinitionProps]:
        '''
        :stability: experimental
        '''
        result = self._values.get("alarms")
        assert result is not None, "Required property 'alarms' is missing"
        return typing.cast(typing.List[AlarmDefinitionProps], result)

    @builtins.property
    def node(self) -> _constructs_77d1e7e8.Construct:
        '''
        :stability: experimental
        '''
        result = self._values.get("node")
        assert result is not None, "Required property 'node' is missing"
        return typing.cast(_constructs_77d1e7e8.Construct, result)

    @builtins.property
    def node_identifier(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("node_identifier")
        assert result is not None, "Required property 'node_identifier' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BuildAlarmsProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(_aws_cdk_ceddda9d.IAspect)
class CacheClusterMonitoringAspect(
    metaclass=jsii.JSIIMeta,
    jsii_type="@condensetech/cdk-constructs.CacheClusterMonitoringAspect",
):
    '''(experimental) The CacheClusterMonitoringAspect iterates over the Elasticache clusters and adds monitoring widgets and alarms.

    :stability: experimental
    '''

    def __init__(self, monitoring_facade: "ICondenseMonitoringFacade") -> None:
        '''
        :param monitoring_facade: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7aef7e87980576bf6891799025cab53dd237cb096ccf028905894401b9349a54)
            check_type(argname="argument monitoring_facade", value=monitoring_facade, expected_type=type_hints["monitoring_facade"])
        jsii.create(self.__class__, self, [monitoring_facade])

    @jsii.member(jsii_name="overrideConfig")
    def override_config(
        self,
        node: _aws_cdk_aws_elasticache_ceddda9d.CfnCacheCluster,
        *,
        cpu_utilization_threshold: typing.Optional[jsii.Number] = None,
        engine_cpu_utilization_threshold: typing.Optional[jsii.Number] = None,
        max_connections_threshold: typing.Optional[jsii.Number] = None,
        memory_usage_threshold: typing.Optional[jsii.Number] = None,
        replication_lag_threshold: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    ) -> None:
        '''(experimental) Overrides the default configuration for a specific Elasticache cluster.

        :param node: The elasticache cluster to monitor.
        :param cpu_utilization_threshold: (experimental) The CPU Utilization (%) threshold. Default: 90
        :param engine_cpu_utilization_threshold: (experimental) The Engine CPU Utilization (%) threshold. Default: 95
        :param max_connections_threshold: (experimental) The Max Connections threshold. Default: 60,000
        :param memory_usage_threshold: (experimental) The Memory Usage (%) threshold. Default: 90
        :param replication_lag_threshold: (experimental) The Replication Lag threshold. Default: - No threshold.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5d896e278ec33d0cf2074937f796f239b7fb8aa49653a46b2f3f4401b5ae50f8)
            check_type(argname="argument node", value=node, expected_type=type_hints["node"])
        config = CacheClusterMonitoringConfig(
            cpu_utilization_threshold=cpu_utilization_threshold,
            engine_cpu_utilization_threshold=engine_cpu_utilization_threshold,
            max_connections_threshold=max_connections_threshold,
            memory_usage_threshold=memory_usage_threshold,
            replication_lag_threshold=replication_lag_threshold,
        )

        return typing.cast(None, jsii.invoke(self, "overrideConfig", [node, config]))

    @jsii.member(jsii_name="visit")
    def visit(self, node: _constructs_77d1e7e8.IConstruct) -> None:
        '''(experimental) All aspects can visit an IConstruct.

        :param node: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b4e5b66f2c71a825830e5ce1ed16e411bf5446d194055bcdfe8ca31aadcf4636)
            check_type(argname="argument node", value=node, expected_type=type_hints["node"])
        return typing.cast(None, jsii.invoke(self, "visit", [node]))

    @builtins.property
    @jsii.member(jsii_name="monitoringFacade")
    def monitoring_facade(self) -> "ICondenseMonitoringFacade":
        '''
        :stability: experimental
        '''
        return typing.cast("ICondenseMonitoringFacade", jsii.get(self, "monitoringFacade"))


@jsii.data_type(
    jsii_type="@condensetech/cdk-constructs.CacheClusterMonitoringConfig",
    jsii_struct_bases=[],
    name_mapping={
        "cpu_utilization_threshold": "cpuUtilizationThreshold",
        "engine_cpu_utilization_threshold": "engineCpuUtilizationThreshold",
        "max_connections_threshold": "maxConnectionsThreshold",
        "memory_usage_threshold": "memoryUsageThreshold",
        "replication_lag_threshold": "replicationLagThreshold",
    },
)
class CacheClusterMonitoringConfig:
    def __init__(
        self,
        *,
        cpu_utilization_threshold: typing.Optional[jsii.Number] = None,
        engine_cpu_utilization_threshold: typing.Optional[jsii.Number] = None,
        max_connections_threshold: typing.Optional[jsii.Number] = None,
        memory_usage_threshold: typing.Optional[jsii.Number] = None,
        replication_lag_threshold: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    ) -> None:
        '''(experimental) The CacheClusterMonitoringConfig defines the thresholds for the cache cluster monitoring.

        :param cpu_utilization_threshold: (experimental) The CPU Utilization (%) threshold. Default: 90
        :param engine_cpu_utilization_threshold: (experimental) The Engine CPU Utilization (%) threshold. Default: 95
        :param max_connections_threshold: (experimental) The Max Connections threshold. Default: 60,000
        :param memory_usage_threshold: (experimental) The Memory Usage (%) threshold. Default: 90
        :param replication_lag_threshold: (experimental) The Replication Lag threshold. Default: - No threshold.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f100edbfc1c3c6e516f7c9dd96a162cd991c46b41383cc0777180f44158595d8)
            check_type(argname="argument cpu_utilization_threshold", value=cpu_utilization_threshold, expected_type=type_hints["cpu_utilization_threshold"])
            check_type(argname="argument engine_cpu_utilization_threshold", value=engine_cpu_utilization_threshold, expected_type=type_hints["engine_cpu_utilization_threshold"])
            check_type(argname="argument max_connections_threshold", value=max_connections_threshold, expected_type=type_hints["max_connections_threshold"])
            check_type(argname="argument memory_usage_threshold", value=memory_usage_threshold, expected_type=type_hints["memory_usage_threshold"])
            check_type(argname="argument replication_lag_threshold", value=replication_lag_threshold, expected_type=type_hints["replication_lag_threshold"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if cpu_utilization_threshold is not None:
            self._values["cpu_utilization_threshold"] = cpu_utilization_threshold
        if engine_cpu_utilization_threshold is not None:
            self._values["engine_cpu_utilization_threshold"] = engine_cpu_utilization_threshold
        if max_connections_threshold is not None:
            self._values["max_connections_threshold"] = max_connections_threshold
        if memory_usage_threshold is not None:
            self._values["memory_usage_threshold"] = memory_usage_threshold
        if replication_lag_threshold is not None:
            self._values["replication_lag_threshold"] = replication_lag_threshold

    @builtins.property
    def cpu_utilization_threshold(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The CPU Utilization (%) threshold.

        :default: 90

        :stability: experimental
        '''
        result = self._values.get("cpu_utilization_threshold")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def engine_cpu_utilization_threshold(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The Engine CPU Utilization (%) threshold.

        :default: 95

        :stability: experimental
        '''
        result = self._values.get("engine_cpu_utilization_threshold")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def max_connections_threshold(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The Max Connections threshold.

        :default: 60,000

        :stability: experimental
        '''
        result = self._values.get("max_connections_threshold")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def memory_usage_threshold(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The Memory Usage (%) threshold.

        :default: 90

        :stability: experimental
        '''
        result = self._values.get("memory_usage_threshold")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def replication_lag_threshold(self) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        '''(experimental) The Replication Lag threshold.

        :default: - No threshold.

        :stability: experimental
        '''
        result = self._values.get("replication_lag_threshold")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CacheClusterMonitoringConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@condensetech/cdk-constructs.CloudwatchAlarmsDiscordConfig",
    jsii_struct_bases=[],
    name_mapping={"webhook": "webhook", "username": "username"},
)
class CloudwatchAlarmsDiscordConfig:
    def __init__(
        self,
        *,
        webhook: builtins.str,
        username: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Discord configuration for the Cloudwatch Alarms Topic.

        :param webhook: 
        :param username: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fdcb0b643b2fafd341022ee345eb921ce9f29aac668330e8eb0f5a143a0a022a)
            check_type(argname="argument webhook", value=webhook, expected_type=type_hints["webhook"])
            check_type(argname="argument username", value=username, expected_type=type_hints["username"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "webhook": webhook,
        }
        if username is not None:
            self._values["username"] = username

    @builtins.property
    def webhook(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("webhook")
        assert result is not None, "Required property 'webhook' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def username(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("username")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CloudwatchAlarmsDiscordConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@condensetech/cdk-constructs.CloudwatchAlarmsSlackConfig",
    jsii_struct_bases=[],
    name_mapping={"webhook": "webhook"},
)
class CloudwatchAlarmsSlackConfig:
    def __init__(self, *, webhook: builtins.str) -> None:
        '''(experimental) Slack configuration for the Cloudwatch Alarms Topic.

        :param webhook: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ca263c8f4b8475c5c6b12308ef78c8e38b325e08b9bd3ae58cb8e3a5cbb048c4)
            check_type(argname="argument webhook", value=webhook, expected_type=type_hints["webhook"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "webhook": webhook,
        }

    @builtins.property
    def webhook(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("webhook")
        assert result is not None, "Required property 'webhook' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CloudwatchAlarmsSlackConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CloudwatchAlarmsTopicStack(
    _aws_cdk_ceddda9d.Stack,
    metaclass=jsii.JSIIMeta,
    jsii_type="@condensetech/cdk-constructs.CloudwatchAlarmsTopicStack",
):
    '''(experimental) The CloudwatchAlarmsTopicStack creates an SNS topic for Cloudwatch alarms.

    The stack  and optionally sends the alarms to Discord or Jira.

    :stability: experimental
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        discord: typing.Optional[typing.Union[CloudwatchAlarmsDiscordConfig, typing.Dict[builtins.str, typing.Any]]] = None,
        jira_subscription_webhook: typing.Optional[builtins.str] = None,
        slack: typing.Optional[typing.Union[CloudwatchAlarmsSlackConfig, typing.Dict[builtins.str, typing.Any]]] = None,
        topic_name: typing.Optional[builtins.str] = None,
        url_subscription_webhooks: typing.Optional[typing.Sequence[builtins.str]] = None,
        analytics_reporting: typing.Optional[builtins.bool] = None,
        cross_region_references: typing.Optional[builtins.bool] = None,
        description: typing.Optional[builtins.str] = None,
        env: typing.Optional[typing.Union[_aws_cdk_ceddda9d.Environment, typing.Dict[builtins.str, typing.Any]]] = None,
        permissions_boundary: typing.Optional[_aws_cdk_ceddda9d.PermissionsBoundary] = None,
        stack_name: typing.Optional[builtins.str] = None,
        suppress_template_indentation: typing.Optional[builtins.bool] = None,
        synthesizer: typing.Optional[_aws_cdk_ceddda9d.IStackSynthesizer] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        termination_protection: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param discord: (experimental) Discord webhook configuration. If provided, the alarms will be sent to the Discord channel.
        :param jira_subscription_webhook: (deprecated) Jira subscription webhook. If provided, the alarms will be sent to Jira.
        :param slack: (experimental) Slack webhook configuration. If provided, the alarms will be sent to the Discord channel.
        :param topic_name: (experimental) The name of the alarms topic. It is recommended to set a name.
        :param url_subscription_webhooks: (experimental) Subscription webhooks. If provided, an HTTP request is made against the provided url with alarm details.
        :param analytics_reporting: Include runtime versioning information in this Stack. Default: ``analyticsReporting`` setting of containing ``App``, or value of 'aws:cdk:version-reporting' context key
        :param cross_region_references: Enable this flag to allow native cross region stack references. Enabling this will create a CloudFormation custom resource in both the producing stack and consuming stack in order to perform the export/import This feature is currently experimental Default: false
        :param description: A description of the stack. Default: - No description.
        :param env: The AWS environment (account/region) where this stack will be deployed. Set the ``region``/``account`` fields of ``env`` to either a concrete value to select the indicated environment (recommended for production stacks), or to the values of environment variables ``CDK_DEFAULT_REGION``/``CDK_DEFAULT_ACCOUNT`` to let the target environment depend on the AWS credentials/configuration that the CDK CLI is executed under (recommended for development stacks). If the ``Stack`` is instantiated inside a ``Stage``, any undefined ``region``/``account`` fields from ``env`` will default to the same field on the encompassing ``Stage``, if configured there. If either ``region`` or ``account`` are not set nor inherited from ``Stage``, the Stack will be considered "*environment-agnostic*"". Environment-agnostic stacks can be deployed to any environment but may not be able to take advantage of all features of the CDK. For example, they will not be able to use environmental context lookups such as ``ec2.Vpc.fromLookup`` and will not automatically translate Service Principals to the right format based on the environment's AWS partition, and other such enhancements. Default: - The environment of the containing ``Stage`` if available, otherwise create the stack will be environment-agnostic.
        :param permissions_boundary: Options for applying a permissions boundary to all IAM Roles and Users created within this Stage. Default: - no permissions boundary is applied
        :param stack_name: Name to deploy the stack with. Default: - Derived from construct path.
        :param suppress_template_indentation: Enable this flag to suppress indentation in generated CloudFormation templates. If not specified, the value of the ``@aws-cdk/core:suppressTemplateIndentation`` context key will be used. If that is not specified, then the default value ``false`` will be used. Default: - the value of ``@aws-cdk/core:suppressTemplateIndentation``, or ``false`` if that is not set.
        :param synthesizer: Synthesis method to use while deploying this stack. The Stack Synthesizer controls aspects of synthesis and deployment, like how assets are referenced and what IAM roles to use. For more information, see the README of the main CDK package. If not specified, the ``defaultStackSynthesizer`` from ``App`` will be used. If that is not specified, ``DefaultStackSynthesizer`` is used if ``@aws-cdk/core:newStyleStackSynthesis`` is set to ``true`` or the CDK major version is v2. In CDK v1 ``LegacyStackSynthesizer`` is the default if no other synthesizer is specified. Default: - The synthesizer specified on ``App``, or ``DefaultStackSynthesizer`` otherwise.
        :param tags: Stack tags that will be applied to all the taggable resources and the stack itself. Default: {}
        :param termination_protection: Whether to enable termination protection for this stack. Default: false

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__57113cf1eb8b5583f1a3b8b5ff0d2aee0a6d1775e0fbb261cde6c8e9cfcd835d)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = CloudwatchAlarmsTopicStackProps(
            discord=discord,
            jira_subscription_webhook=jira_subscription_webhook,
            slack=slack,
            topic_name=topic_name,
            url_subscription_webhooks=url_subscription_webhooks,
            analytics_reporting=analytics_reporting,
            cross_region_references=cross_region_references,
            description=description,
            env=env,
            permissions_boundary=permissions_boundary,
            stack_name=stack_name,
            suppress_template_indentation=suppress_template_indentation,
            synthesizer=synthesizer,
            tags=tags,
            termination_protection=termination_protection,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property
    @jsii.member(jsii_name="alarmsTopic")
    def alarms_topic(self) -> _aws_cdk_aws_sns_ceddda9d.Topic:
        '''
        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_sns_ceddda9d.Topic, jsii.get(self, "alarmsTopic"))


@jsii.data_type(
    jsii_type="@condensetech/cdk-constructs.CloudwatchAlarmsTopicStackProps",
    jsii_struct_bases=[_aws_cdk_ceddda9d.StackProps],
    name_mapping={
        "analytics_reporting": "analyticsReporting",
        "cross_region_references": "crossRegionReferences",
        "description": "description",
        "env": "env",
        "permissions_boundary": "permissionsBoundary",
        "stack_name": "stackName",
        "suppress_template_indentation": "suppressTemplateIndentation",
        "synthesizer": "synthesizer",
        "tags": "tags",
        "termination_protection": "terminationProtection",
        "discord": "discord",
        "jira_subscription_webhook": "jiraSubscriptionWebhook",
        "slack": "slack",
        "topic_name": "topicName",
        "url_subscription_webhooks": "urlSubscriptionWebhooks",
    },
)
class CloudwatchAlarmsTopicStackProps(_aws_cdk_ceddda9d.StackProps):
    def __init__(
        self,
        *,
        analytics_reporting: typing.Optional[builtins.bool] = None,
        cross_region_references: typing.Optional[builtins.bool] = None,
        description: typing.Optional[builtins.str] = None,
        env: typing.Optional[typing.Union[_aws_cdk_ceddda9d.Environment, typing.Dict[builtins.str, typing.Any]]] = None,
        permissions_boundary: typing.Optional[_aws_cdk_ceddda9d.PermissionsBoundary] = None,
        stack_name: typing.Optional[builtins.str] = None,
        suppress_template_indentation: typing.Optional[builtins.bool] = None,
        synthesizer: typing.Optional[_aws_cdk_ceddda9d.IStackSynthesizer] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        termination_protection: typing.Optional[builtins.bool] = None,
        discord: typing.Optional[typing.Union[CloudwatchAlarmsDiscordConfig, typing.Dict[builtins.str, typing.Any]]] = None,
        jira_subscription_webhook: typing.Optional[builtins.str] = None,
        slack: typing.Optional[typing.Union[CloudwatchAlarmsSlackConfig, typing.Dict[builtins.str, typing.Any]]] = None,
        topic_name: typing.Optional[builtins.str] = None,
        url_subscription_webhooks: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''(experimental) Properties for the CloudwatchAlarmsTopicStack.

        :param analytics_reporting: Include runtime versioning information in this Stack. Default: ``analyticsReporting`` setting of containing ``App``, or value of 'aws:cdk:version-reporting' context key
        :param cross_region_references: Enable this flag to allow native cross region stack references. Enabling this will create a CloudFormation custom resource in both the producing stack and consuming stack in order to perform the export/import This feature is currently experimental Default: false
        :param description: A description of the stack. Default: - No description.
        :param env: The AWS environment (account/region) where this stack will be deployed. Set the ``region``/``account`` fields of ``env`` to either a concrete value to select the indicated environment (recommended for production stacks), or to the values of environment variables ``CDK_DEFAULT_REGION``/``CDK_DEFAULT_ACCOUNT`` to let the target environment depend on the AWS credentials/configuration that the CDK CLI is executed under (recommended for development stacks). If the ``Stack`` is instantiated inside a ``Stage``, any undefined ``region``/``account`` fields from ``env`` will default to the same field on the encompassing ``Stage``, if configured there. If either ``region`` or ``account`` are not set nor inherited from ``Stage``, the Stack will be considered "*environment-agnostic*"". Environment-agnostic stacks can be deployed to any environment but may not be able to take advantage of all features of the CDK. For example, they will not be able to use environmental context lookups such as ``ec2.Vpc.fromLookup`` and will not automatically translate Service Principals to the right format based on the environment's AWS partition, and other such enhancements. Default: - The environment of the containing ``Stage`` if available, otherwise create the stack will be environment-agnostic.
        :param permissions_boundary: Options for applying a permissions boundary to all IAM Roles and Users created within this Stage. Default: - no permissions boundary is applied
        :param stack_name: Name to deploy the stack with. Default: - Derived from construct path.
        :param suppress_template_indentation: Enable this flag to suppress indentation in generated CloudFormation templates. If not specified, the value of the ``@aws-cdk/core:suppressTemplateIndentation`` context key will be used. If that is not specified, then the default value ``false`` will be used. Default: - the value of ``@aws-cdk/core:suppressTemplateIndentation``, or ``false`` if that is not set.
        :param synthesizer: Synthesis method to use while deploying this stack. The Stack Synthesizer controls aspects of synthesis and deployment, like how assets are referenced and what IAM roles to use. For more information, see the README of the main CDK package. If not specified, the ``defaultStackSynthesizer`` from ``App`` will be used. If that is not specified, ``DefaultStackSynthesizer`` is used if ``@aws-cdk/core:newStyleStackSynthesis`` is set to ``true`` or the CDK major version is v2. In CDK v1 ``LegacyStackSynthesizer`` is the default if no other synthesizer is specified. Default: - The synthesizer specified on ``App``, or ``DefaultStackSynthesizer`` otherwise.
        :param tags: Stack tags that will be applied to all the taggable resources and the stack itself. Default: {}
        :param termination_protection: Whether to enable termination protection for this stack. Default: false
        :param discord: (experimental) Discord webhook configuration. If provided, the alarms will be sent to the Discord channel.
        :param jira_subscription_webhook: (deprecated) Jira subscription webhook. If provided, the alarms will be sent to Jira.
        :param slack: (experimental) Slack webhook configuration. If provided, the alarms will be sent to the Discord channel.
        :param topic_name: (experimental) The name of the alarms topic. It is recommended to set a name.
        :param url_subscription_webhooks: (experimental) Subscription webhooks. If provided, an HTTP request is made against the provided url with alarm details.

        :stability: experimental
        '''
        if isinstance(env, dict):
            env = _aws_cdk_ceddda9d.Environment(**env)
        if isinstance(discord, dict):
            discord = CloudwatchAlarmsDiscordConfig(**discord)
        if isinstance(slack, dict):
            slack = CloudwatchAlarmsSlackConfig(**slack)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0681772f7ea86b94082174f0e8837e8be9423519730e5fb2d137a83caaa8503d)
            check_type(argname="argument analytics_reporting", value=analytics_reporting, expected_type=type_hints["analytics_reporting"])
            check_type(argname="argument cross_region_references", value=cross_region_references, expected_type=type_hints["cross_region_references"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument env", value=env, expected_type=type_hints["env"])
            check_type(argname="argument permissions_boundary", value=permissions_boundary, expected_type=type_hints["permissions_boundary"])
            check_type(argname="argument stack_name", value=stack_name, expected_type=type_hints["stack_name"])
            check_type(argname="argument suppress_template_indentation", value=suppress_template_indentation, expected_type=type_hints["suppress_template_indentation"])
            check_type(argname="argument synthesizer", value=synthesizer, expected_type=type_hints["synthesizer"])
            check_type(argname="argument tags", value=tags, expected_type=type_hints["tags"])
            check_type(argname="argument termination_protection", value=termination_protection, expected_type=type_hints["termination_protection"])
            check_type(argname="argument discord", value=discord, expected_type=type_hints["discord"])
            check_type(argname="argument jira_subscription_webhook", value=jira_subscription_webhook, expected_type=type_hints["jira_subscription_webhook"])
            check_type(argname="argument slack", value=slack, expected_type=type_hints["slack"])
            check_type(argname="argument topic_name", value=topic_name, expected_type=type_hints["topic_name"])
            check_type(argname="argument url_subscription_webhooks", value=url_subscription_webhooks, expected_type=type_hints["url_subscription_webhooks"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if analytics_reporting is not None:
            self._values["analytics_reporting"] = analytics_reporting
        if cross_region_references is not None:
            self._values["cross_region_references"] = cross_region_references
        if description is not None:
            self._values["description"] = description
        if env is not None:
            self._values["env"] = env
        if permissions_boundary is not None:
            self._values["permissions_boundary"] = permissions_boundary
        if stack_name is not None:
            self._values["stack_name"] = stack_name
        if suppress_template_indentation is not None:
            self._values["suppress_template_indentation"] = suppress_template_indentation
        if synthesizer is not None:
            self._values["synthesizer"] = synthesizer
        if tags is not None:
            self._values["tags"] = tags
        if termination_protection is not None:
            self._values["termination_protection"] = termination_protection
        if discord is not None:
            self._values["discord"] = discord
        if jira_subscription_webhook is not None:
            self._values["jira_subscription_webhook"] = jira_subscription_webhook
        if slack is not None:
            self._values["slack"] = slack
        if topic_name is not None:
            self._values["topic_name"] = topic_name
        if url_subscription_webhooks is not None:
            self._values["url_subscription_webhooks"] = url_subscription_webhooks

    @builtins.property
    def analytics_reporting(self) -> typing.Optional[builtins.bool]:
        '''Include runtime versioning information in this Stack.

        :default:

        ``analyticsReporting`` setting of containing ``App``, or value of
        'aws:cdk:version-reporting' context key
        '''
        result = self._values.get("analytics_reporting")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def cross_region_references(self) -> typing.Optional[builtins.bool]:
        '''Enable this flag to allow native cross region stack references.

        Enabling this will create a CloudFormation custom resource
        in both the producing stack and consuming stack in order to perform the export/import

        This feature is currently experimental

        :default: false
        '''
        result = self._values.get("cross_region_references")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''A description of the stack.

        :default: - No description.
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def env(self) -> typing.Optional[_aws_cdk_ceddda9d.Environment]:
        '''The AWS environment (account/region) where this stack will be deployed.

        Set the ``region``/``account`` fields of ``env`` to either a concrete value to
        select the indicated environment (recommended for production stacks), or to
        the values of environment variables
        ``CDK_DEFAULT_REGION``/``CDK_DEFAULT_ACCOUNT`` to let the target environment
        depend on the AWS credentials/configuration that the CDK CLI is executed
        under (recommended for development stacks).

        If the ``Stack`` is instantiated inside a ``Stage``, any undefined
        ``region``/``account`` fields from ``env`` will default to the same field on the
        encompassing ``Stage``, if configured there.

        If either ``region`` or ``account`` are not set nor inherited from ``Stage``, the
        Stack will be considered "*environment-agnostic*"". Environment-agnostic
        stacks can be deployed to any environment but may not be able to take
        advantage of all features of the CDK. For example, they will not be able to
        use environmental context lookups such as ``ec2.Vpc.fromLookup`` and will not
        automatically translate Service Principals to the right format based on the
        environment's AWS partition, and other such enhancements.

        :default:

        - The environment of the containing ``Stage`` if available,
        otherwise create the stack will be environment-agnostic.

        Example::

            // Use a concrete account and region to deploy this stack to:
            // `.account` and `.region` will simply return these values.
            new Stack(app, 'Stack1', {
              env: {
                account: '123456789012',
                region: 'us-east-1'
              },
            });
            
            // Use the CLI's current credentials to determine the target environment:
            // `.account` and `.region` will reflect the account+region the CLI
            // is configured to use (based on the user CLI credentials)
            new Stack(app, 'Stack2', {
              env: {
                account: process.env.CDK_DEFAULT_ACCOUNT,
                region: process.env.CDK_DEFAULT_REGION
              },
            });
            
            // Define multiple stacks stage associated with an environment
            const myStage = new Stage(app, 'MyStage', {
              env: {
                account: '123456789012',
                region: 'us-east-1'
              }
            });
            
            // both of these stacks will use the stage's account/region:
            // `.account` and `.region` will resolve to the concrete values as above
            new MyStack(myStage, 'Stack1');
            new YourStack(myStage, 'Stack2');
            
            // Define an environment-agnostic stack:
            // `.account` and `.region` will resolve to `{ "Ref": "AWS::AccountId" }` and `{ "Ref": "AWS::Region" }` respectively.
            // which will only resolve to actual values by CloudFormation during deployment.
            new MyStack(app, 'Stack1');
        '''
        result = self._values.get("env")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Environment], result)

    @builtins.property
    def permissions_boundary(
        self,
    ) -> typing.Optional[_aws_cdk_ceddda9d.PermissionsBoundary]:
        '''Options for applying a permissions boundary to all IAM Roles and Users created within this Stage.

        :default: - no permissions boundary is applied
        '''
        result = self._values.get("permissions_boundary")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.PermissionsBoundary], result)

    @builtins.property
    def stack_name(self) -> typing.Optional[builtins.str]:
        '''Name to deploy the stack with.

        :default: - Derived from construct path.
        '''
        result = self._values.get("stack_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def suppress_template_indentation(self) -> typing.Optional[builtins.bool]:
        '''Enable this flag to suppress indentation in generated CloudFormation templates.

        If not specified, the value of the ``@aws-cdk/core:suppressTemplateIndentation``
        context key will be used. If that is not specified, then the
        default value ``false`` will be used.

        :default: - the value of ``@aws-cdk/core:suppressTemplateIndentation``, or ``false`` if that is not set.
        '''
        result = self._values.get("suppress_template_indentation")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def synthesizer(self) -> typing.Optional[_aws_cdk_ceddda9d.IStackSynthesizer]:
        '''Synthesis method to use while deploying this stack.

        The Stack Synthesizer controls aspects of synthesis and deployment,
        like how assets are referenced and what IAM roles to use. For more
        information, see the README of the main CDK package.

        If not specified, the ``defaultStackSynthesizer`` from ``App`` will be used.
        If that is not specified, ``DefaultStackSynthesizer`` is used if
        ``@aws-cdk/core:newStyleStackSynthesis`` is set to ``true`` or the CDK major
        version is v2. In CDK v1 ``LegacyStackSynthesizer`` is the default if no
        other synthesizer is specified.

        :default: - The synthesizer specified on ``App``, or ``DefaultStackSynthesizer`` otherwise.
        '''
        result = self._values.get("synthesizer")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.IStackSynthesizer], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Stack tags that will be applied to all the taggable resources and the stack itself.

        :default: {}
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def termination_protection(self) -> typing.Optional[builtins.bool]:
        '''Whether to enable termination protection for this stack.

        :default: false
        '''
        result = self._values.get("termination_protection")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def discord(self) -> typing.Optional[CloudwatchAlarmsDiscordConfig]:
        '''(experimental) Discord webhook configuration.

        If provided, the alarms will be sent to the Discord channel.

        :stability: experimental
        '''
        result = self._values.get("discord")
        return typing.cast(typing.Optional[CloudwatchAlarmsDiscordConfig], result)

    @builtins.property
    def jira_subscription_webhook(self) -> typing.Optional[builtins.str]:
        '''(deprecated) Jira subscription webhook.

        If provided, the alarms will be sent to Jira.

        :deprecated: Use ``urlSubscriptionWebhooks`` instead.

        :stability: deprecated
        '''
        result = self._values.get("jira_subscription_webhook")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def slack(self) -> typing.Optional[CloudwatchAlarmsSlackConfig]:
        '''(experimental) Slack webhook configuration.

        If provided, the alarms will be sent to the Discord channel.

        :stability: experimental
        '''
        result = self._values.get("slack")
        return typing.cast(typing.Optional[CloudwatchAlarmsSlackConfig], result)

    @builtins.property
    def topic_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of the alarms topic.

        It is recommended to set a name.

        :stability: experimental
        '''
        result = self._values.get("topic_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def url_subscription_webhooks(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) Subscription webhooks.

        If provided, an HTTP request is made against the provided url with alarm details.

        :stability: experimental
        '''
        result = self._values.get("url_subscription_webhooks")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CloudwatchAlarmsTopicStackProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@condensetech/cdk-constructs.DatabaseInstanceProps",
    jsii_struct_bases=[],
    name_mapping={
        "engine": "engine",
        "networking": "networking",
        "allocated_storage": "allocatedStorage",
        "allow_major_version_upgrade": "allowMajorVersionUpgrade",
        "backup_retention": "backupRetention",
        "cloudwatch_logs_exports": "cloudwatchLogsExports",
        "cloudwatch_logs_retention": "cloudwatchLogsRetention",
        "credentials_secret_name": "credentialsSecretName",
        "credentials_username": "credentialsUsername",
        "database_name": "databaseName",
        "enable_performance_insights": "enablePerformanceInsights",
        "instance_identifier": "instanceIdentifier",
        "instance_type": "instanceType",
        "max_allocated_storage": "maxAllocatedStorage",
        "multi_az": "multiAz",
        "parameters": "parameters",
        "removal_policy": "removalPolicy",
        "security_group_name": "securityGroupName",
        "storage_type": "storageType",
    },
)
class DatabaseInstanceProps:
    def __init__(
        self,
        *,
        engine: _aws_cdk_aws_rds_ceddda9d.IInstanceEngine,
        networking: "INetworking",
        allocated_storage: typing.Optional[jsii.Number] = None,
        allow_major_version_upgrade: typing.Optional[builtins.bool] = None,
        backup_retention: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        cloudwatch_logs_exports: typing.Optional[typing.Sequence[builtins.str]] = None,
        cloudwatch_logs_retention: typing.Optional[_aws_cdk_aws_logs_ceddda9d.RetentionDays] = None,
        credentials_secret_name: typing.Optional[builtins.str] = None,
        credentials_username: typing.Optional[builtins.str] = None,
        database_name: typing.Optional[builtins.str] = None,
        enable_performance_insights: typing.Optional[builtins.bool] = None,
        instance_identifier: typing.Optional[builtins.str] = None,
        instance_type: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.InstanceType] = None,
        max_allocated_storage: typing.Optional[jsii.Number] = None,
        multi_az: typing.Optional[builtins.bool] = None,
        parameters: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
        security_group_name: typing.Optional[builtins.str] = None,
        storage_type: typing.Optional[_aws_cdk_aws_rds_ceddda9d.StorageType] = None,
    ) -> None:
        '''(experimental) Properties for the DatabaseInstance construct.

        :param engine: (experimental) The engine of the database instance.
        :param networking: (experimental) The networking configuration for the database instance.
        :param allocated_storage: (experimental) The allocated storage of the database instance. Default: 20
        :param allow_major_version_upgrade: (experimental) Whether to allow major version upgrades. Default: false
        :param backup_retention: (experimental) The backup retention period. Default: - It uses the default applied by [rds.DatabaseInstanceProps#backupRetention]https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_rds.DatabaseInstanceProps.html#backupretention).
        :param cloudwatch_logs_exports: (experimental) The list of log types that need to be enabled for exporting to CloudWatch Logs. Default: - No log types are enabled.
        :param cloudwatch_logs_retention: (experimental) The number of days log events are kept in CloudWatch Logs. When updating this property, unsetting it doesn't remove the log retention policy. To remove the retention policy, set the value to Infinity. Default: logs never expire
        :param credentials_secret_name: (experimental) The name of the secret that stores the credentials of the database. Default: ``${construct.node.path}/secret``
        :param credentials_username: (experimental) The username of the database. Default: db_user
        :param database_name: (experimental) The name of the database. Default: - No default database is created.
        :param enable_performance_insights: (experimental) Whether to enable Performance Insights. Default: false
        :param instance_identifier: (experimental) The identifier of the database instance. Default: - No identifier is specified.
        :param instance_type: (experimental) The instance type of the database instance. Default: - db.t3.small.
        :param max_allocated_storage: (experimental) The maximum allocated storage of the database instance. Default: - No maximum allocated storage is specified.
        :param multi_az: (experimental) If the database instance is multi-AZ. Default: false
        :param parameters: (experimental) The parameters to override in the parameter group. Default: - No parameter is overridden.
        :param removal_policy: (experimental) The removal policy to apply when the cluster is removed. Default: RemovalPolicy.RETAIN
        :param security_group_name: (experimental) The name of the security group. Default: - ``${construct.node.path}-sg``.
        :param storage_type: (experimental) The storage type of the database instance. Default: rds.StorageType.GP3

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a7e78fb9d1c1440969aaea6b5f1207d42b7080de9a6db81dca390dd6232c8cf9)
            check_type(argname="argument engine", value=engine, expected_type=type_hints["engine"])
            check_type(argname="argument networking", value=networking, expected_type=type_hints["networking"])
            check_type(argname="argument allocated_storage", value=allocated_storage, expected_type=type_hints["allocated_storage"])
            check_type(argname="argument allow_major_version_upgrade", value=allow_major_version_upgrade, expected_type=type_hints["allow_major_version_upgrade"])
            check_type(argname="argument backup_retention", value=backup_retention, expected_type=type_hints["backup_retention"])
            check_type(argname="argument cloudwatch_logs_exports", value=cloudwatch_logs_exports, expected_type=type_hints["cloudwatch_logs_exports"])
            check_type(argname="argument cloudwatch_logs_retention", value=cloudwatch_logs_retention, expected_type=type_hints["cloudwatch_logs_retention"])
            check_type(argname="argument credentials_secret_name", value=credentials_secret_name, expected_type=type_hints["credentials_secret_name"])
            check_type(argname="argument credentials_username", value=credentials_username, expected_type=type_hints["credentials_username"])
            check_type(argname="argument database_name", value=database_name, expected_type=type_hints["database_name"])
            check_type(argname="argument enable_performance_insights", value=enable_performance_insights, expected_type=type_hints["enable_performance_insights"])
            check_type(argname="argument instance_identifier", value=instance_identifier, expected_type=type_hints["instance_identifier"])
            check_type(argname="argument instance_type", value=instance_type, expected_type=type_hints["instance_type"])
            check_type(argname="argument max_allocated_storage", value=max_allocated_storage, expected_type=type_hints["max_allocated_storage"])
            check_type(argname="argument multi_az", value=multi_az, expected_type=type_hints["multi_az"])
            check_type(argname="argument parameters", value=parameters, expected_type=type_hints["parameters"])
            check_type(argname="argument removal_policy", value=removal_policy, expected_type=type_hints["removal_policy"])
            check_type(argname="argument security_group_name", value=security_group_name, expected_type=type_hints["security_group_name"])
            check_type(argname="argument storage_type", value=storage_type, expected_type=type_hints["storage_type"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "engine": engine,
            "networking": networking,
        }
        if allocated_storage is not None:
            self._values["allocated_storage"] = allocated_storage
        if allow_major_version_upgrade is not None:
            self._values["allow_major_version_upgrade"] = allow_major_version_upgrade
        if backup_retention is not None:
            self._values["backup_retention"] = backup_retention
        if cloudwatch_logs_exports is not None:
            self._values["cloudwatch_logs_exports"] = cloudwatch_logs_exports
        if cloudwatch_logs_retention is not None:
            self._values["cloudwatch_logs_retention"] = cloudwatch_logs_retention
        if credentials_secret_name is not None:
            self._values["credentials_secret_name"] = credentials_secret_name
        if credentials_username is not None:
            self._values["credentials_username"] = credentials_username
        if database_name is not None:
            self._values["database_name"] = database_name
        if enable_performance_insights is not None:
            self._values["enable_performance_insights"] = enable_performance_insights
        if instance_identifier is not None:
            self._values["instance_identifier"] = instance_identifier
        if instance_type is not None:
            self._values["instance_type"] = instance_type
        if max_allocated_storage is not None:
            self._values["max_allocated_storage"] = max_allocated_storage
        if multi_az is not None:
            self._values["multi_az"] = multi_az
        if parameters is not None:
            self._values["parameters"] = parameters
        if removal_policy is not None:
            self._values["removal_policy"] = removal_policy
        if security_group_name is not None:
            self._values["security_group_name"] = security_group_name
        if storage_type is not None:
            self._values["storage_type"] = storage_type

    @builtins.property
    def engine(self) -> _aws_cdk_aws_rds_ceddda9d.IInstanceEngine:
        '''(experimental) The engine of the database instance.

        :stability: experimental
        '''
        result = self._values.get("engine")
        assert result is not None, "Required property 'engine' is missing"
        return typing.cast(_aws_cdk_aws_rds_ceddda9d.IInstanceEngine, result)

    @builtins.property
    def networking(self) -> "INetworking":
        '''(experimental) The networking configuration for the database instance.

        :stability: experimental
        '''
        result = self._values.get("networking")
        assert result is not None, "Required property 'networking' is missing"
        return typing.cast("INetworking", result)

    @builtins.property
    def allocated_storage(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The allocated storage of the database instance.

        :default: 20

        :stability: experimental
        '''
        result = self._values.get("allocated_storage")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def allow_major_version_upgrade(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Whether to allow major version upgrades.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("allow_major_version_upgrade")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def backup_retention(self) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        '''(experimental) The backup retention period.

        :default: - It uses the default applied by [rds.DatabaseInstanceProps#backupRetention]https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_rds.DatabaseInstanceProps.html#backupretention).

        :stability: experimental
        '''
        result = self._values.get("backup_retention")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], result)

    @builtins.property
    def cloudwatch_logs_exports(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) The list of log types that need to be enabled for exporting to CloudWatch Logs.

        :default: - No log types are enabled.

        :stability: experimental
        '''
        result = self._values.get("cloudwatch_logs_exports")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def cloudwatch_logs_retention(
        self,
    ) -> typing.Optional[_aws_cdk_aws_logs_ceddda9d.RetentionDays]:
        '''(experimental) The number of days log events are kept in CloudWatch Logs.

        When updating this property, unsetting it doesn't remove the log retention policy. To remove the retention policy, set the value to Infinity.

        :default: logs never expire

        :stability: experimental
        '''
        result = self._values.get("cloudwatch_logs_retention")
        return typing.cast(typing.Optional[_aws_cdk_aws_logs_ceddda9d.RetentionDays], result)

    @builtins.property
    def credentials_secret_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of the secret that stores the credentials of the database.

        :default: ``${construct.node.path}/secret``

        :stability: experimental
        '''
        result = self._values.get("credentials_secret_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def credentials_username(self) -> typing.Optional[builtins.str]:
        '''(experimental) The username of the database.

        :default: db_user

        :stability: experimental
        '''
        result = self._values.get("credentials_username")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def database_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of the database.

        :default: - No default database is created.

        :stability: experimental
        '''
        result = self._values.get("database_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def enable_performance_insights(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Whether to enable Performance Insights.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("enable_performance_insights")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def instance_identifier(self) -> typing.Optional[builtins.str]:
        '''(experimental) The identifier of the database instance.

        :default: - No identifier is specified.

        :stability: experimental
        '''
        result = self._values.get("instance_identifier")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def instance_type(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.InstanceType]:
        '''(experimental) The instance type of the database instance.

        :default: - db.t3.small.

        :stability: experimental
        '''
        result = self._values.get("instance_type")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.InstanceType], result)

    @builtins.property
    def max_allocated_storage(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The maximum allocated storage of the database instance.

        :default: - No maximum allocated storage is specified.

        :stability: experimental
        '''
        result = self._values.get("max_allocated_storage")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def multi_az(self) -> typing.Optional[builtins.bool]:
        '''(experimental) If the database instance is multi-AZ.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("multi_az")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def parameters(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''(experimental) The parameters to override in the parameter group.

        :default: - No parameter is overridden.

        :stability: experimental
        '''
        result = self._values.get("parameters")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def removal_policy(self) -> typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy]:
        '''(experimental) The removal policy to apply when the cluster is removed.

        :default: RemovalPolicy.RETAIN

        :stability: experimental
        '''
        result = self._values.get("removal_policy")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy], result)

    @builtins.property
    def security_group_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of the security group.

        :default: - ``${construct.node.path}-sg``.

        :stability: experimental
        '''
        result = self._values.get("security_group_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def storage_type(self) -> typing.Optional[_aws_cdk_aws_rds_ceddda9d.StorageType]:
        '''(experimental) The storage type of the database instance.

        :default: rds.StorageType.GP3

        :stability: experimental
        '''
        result = self._values.get("storage_type")
        return typing.cast(typing.Optional[_aws_cdk_aws_rds_ceddda9d.StorageType], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DatabaseInstanceProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@condensetech/cdk-constructs.DatabaseInstanceStackProps",
    jsii_struct_bases=[DatabaseInstanceProps, _aws_cdk_ceddda9d.StackProps],
    name_mapping={
        "engine": "engine",
        "networking": "networking",
        "allocated_storage": "allocatedStorage",
        "allow_major_version_upgrade": "allowMajorVersionUpgrade",
        "backup_retention": "backupRetention",
        "cloudwatch_logs_exports": "cloudwatchLogsExports",
        "cloudwatch_logs_retention": "cloudwatchLogsRetention",
        "credentials_secret_name": "credentialsSecretName",
        "credentials_username": "credentialsUsername",
        "database_name": "databaseName",
        "enable_performance_insights": "enablePerformanceInsights",
        "instance_identifier": "instanceIdentifier",
        "instance_type": "instanceType",
        "max_allocated_storage": "maxAllocatedStorage",
        "multi_az": "multiAz",
        "parameters": "parameters",
        "removal_policy": "removalPolicy",
        "security_group_name": "securityGroupName",
        "storage_type": "storageType",
        "analytics_reporting": "analyticsReporting",
        "cross_region_references": "crossRegionReferences",
        "description": "description",
        "env": "env",
        "permissions_boundary": "permissionsBoundary",
        "stack_name": "stackName",
        "suppress_template_indentation": "suppressTemplateIndentation",
        "synthesizer": "synthesizer",
        "tags": "tags",
        "termination_protection": "terminationProtection",
        "monitoring": "monitoring",
    },
)
class DatabaseInstanceStackProps(DatabaseInstanceProps, _aws_cdk_ceddda9d.StackProps):
    def __init__(
        self,
        *,
        engine: _aws_cdk_aws_rds_ceddda9d.IInstanceEngine,
        networking: "INetworking",
        allocated_storage: typing.Optional[jsii.Number] = None,
        allow_major_version_upgrade: typing.Optional[builtins.bool] = None,
        backup_retention: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        cloudwatch_logs_exports: typing.Optional[typing.Sequence[builtins.str]] = None,
        cloudwatch_logs_retention: typing.Optional[_aws_cdk_aws_logs_ceddda9d.RetentionDays] = None,
        credentials_secret_name: typing.Optional[builtins.str] = None,
        credentials_username: typing.Optional[builtins.str] = None,
        database_name: typing.Optional[builtins.str] = None,
        enable_performance_insights: typing.Optional[builtins.bool] = None,
        instance_identifier: typing.Optional[builtins.str] = None,
        instance_type: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.InstanceType] = None,
        max_allocated_storage: typing.Optional[jsii.Number] = None,
        multi_az: typing.Optional[builtins.bool] = None,
        parameters: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
        security_group_name: typing.Optional[builtins.str] = None,
        storage_type: typing.Optional[_aws_cdk_aws_rds_ceddda9d.StorageType] = None,
        analytics_reporting: typing.Optional[builtins.bool] = None,
        cross_region_references: typing.Optional[builtins.bool] = None,
        description: typing.Optional[builtins.str] = None,
        env: typing.Optional[typing.Union[_aws_cdk_ceddda9d.Environment, typing.Dict[builtins.str, typing.Any]]] = None,
        permissions_boundary: typing.Optional[_aws_cdk_ceddda9d.PermissionsBoundary] = None,
        stack_name: typing.Optional[builtins.str] = None,
        suppress_template_indentation: typing.Optional[builtins.bool] = None,
        synthesizer: typing.Optional[_aws_cdk_ceddda9d.IStackSynthesizer] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        termination_protection: typing.Optional[builtins.bool] = None,
        monitoring: typing.Optional[typing.Union["MonitoringFacadeProps", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''(experimental) Properties for the DatabaseInstanceStack.

        :param engine: (experimental) The engine of the database instance.
        :param networking: (experimental) The networking configuration for the database instance.
        :param allocated_storage: (experimental) The allocated storage of the database instance. Default: 20
        :param allow_major_version_upgrade: (experimental) Whether to allow major version upgrades. Default: false
        :param backup_retention: (experimental) The backup retention period. Default: - It uses the default applied by [rds.DatabaseInstanceProps#backupRetention]https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_rds.DatabaseInstanceProps.html#backupretention).
        :param cloudwatch_logs_exports: (experimental) The list of log types that need to be enabled for exporting to CloudWatch Logs. Default: - No log types are enabled.
        :param cloudwatch_logs_retention: (experimental) The number of days log events are kept in CloudWatch Logs. When updating this property, unsetting it doesn't remove the log retention policy. To remove the retention policy, set the value to Infinity. Default: logs never expire
        :param credentials_secret_name: (experimental) The name of the secret that stores the credentials of the database. Default: ``${construct.node.path}/secret``
        :param credentials_username: (experimental) The username of the database. Default: db_user
        :param database_name: (experimental) The name of the database. Default: - No default database is created.
        :param enable_performance_insights: (experimental) Whether to enable Performance Insights. Default: false
        :param instance_identifier: (experimental) The identifier of the database instance. Default: - No identifier is specified.
        :param instance_type: (experimental) The instance type of the database instance. Default: - db.t3.small.
        :param max_allocated_storage: (experimental) The maximum allocated storage of the database instance. Default: - No maximum allocated storage is specified.
        :param multi_az: (experimental) If the database instance is multi-AZ. Default: false
        :param parameters: (experimental) The parameters to override in the parameter group. Default: - No parameter is overridden.
        :param removal_policy: (experimental) The removal policy to apply when the cluster is removed. Default: RemovalPolicy.RETAIN
        :param security_group_name: (experimental) The name of the security group. Default: - ``${construct.node.path}-sg``.
        :param storage_type: (experimental) The storage type of the database instance. Default: rds.StorageType.GP3
        :param analytics_reporting: Include runtime versioning information in this Stack. Default: ``analyticsReporting`` setting of containing ``App``, or value of 'aws:cdk:version-reporting' context key
        :param cross_region_references: Enable this flag to allow native cross region stack references. Enabling this will create a CloudFormation custom resource in both the producing stack and consuming stack in order to perform the export/import This feature is currently experimental Default: false
        :param description: A description of the stack. Default: - No description.
        :param env: The AWS environment (account/region) where this stack will be deployed. Set the ``region``/``account`` fields of ``env`` to either a concrete value to select the indicated environment (recommended for production stacks), or to the values of environment variables ``CDK_DEFAULT_REGION``/``CDK_DEFAULT_ACCOUNT`` to let the target environment depend on the AWS credentials/configuration that the CDK CLI is executed under (recommended for development stacks). If the ``Stack`` is instantiated inside a ``Stage``, any undefined ``region``/``account`` fields from ``env`` will default to the same field on the encompassing ``Stage``, if configured there. If either ``region`` or ``account`` are not set nor inherited from ``Stage``, the Stack will be considered "*environment-agnostic*"". Environment-agnostic stacks can be deployed to any environment but may not be able to take advantage of all features of the CDK. For example, they will not be able to use environmental context lookups such as ``ec2.Vpc.fromLookup`` and will not automatically translate Service Principals to the right format based on the environment's AWS partition, and other such enhancements. Default: - The environment of the containing ``Stage`` if available, otherwise create the stack will be environment-agnostic.
        :param permissions_boundary: Options for applying a permissions boundary to all IAM Roles and Users created within this Stage. Default: - no permissions boundary is applied
        :param stack_name: Name to deploy the stack with. Default: - Derived from construct path.
        :param suppress_template_indentation: Enable this flag to suppress indentation in generated CloudFormation templates. If not specified, the value of the ``@aws-cdk/core:suppressTemplateIndentation`` context key will be used. If that is not specified, then the default value ``false`` will be used. Default: - the value of ``@aws-cdk/core:suppressTemplateIndentation``, or ``false`` if that is not set.
        :param synthesizer: Synthesis method to use while deploying this stack. The Stack Synthesizer controls aspects of synthesis and deployment, like how assets are referenced and what IAM roles to use. For more information, see the README of the main CDK package. If not specified, the ``defaultStackSynthesizer`` from ``App`` will be used. If that is not specified, ``DefaultStackSynthesizer`` is used if ``@aws-cdk/core:newStyleStackSynthesis`` is set to ``true`` or the CDK major version is v2. In CDK v1 ``LegacyStackSynthesizer`` is the default if no other synthesizer is specified. Default: - The synthesizer specified on ``App``, or ``DefaultStackSynthesizer`` otherwise.
        :param tags: Stack tags that will be applied to all the taggable resources and the stack itself. Default: {}
        :param termination_protection: Whether to enable termination protection for this stack. Default: false
        :param monitoring: (experimental) The monitoring configuration to apply to this stack. Default: - No monitoring.

        :stability: experimental
        '''
        if isinstance(env, dict):
            env = _aws_cdk_ceddda9d.Environment(**env)
        if isinstance(monitoring, dict):
            monitoring = MonitoringFacadeProps(**monitoring)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__78f8facc5fb08045f0a685c1db7239710d0c81292514a8db2855f969f9697d10)
            check_type(argname="argument engine", value=engine, expected_type=type_hints["engine"])
            check_type(argname="argument networking", value=networking, expected_type=type_hints["networking"])
            check_type(argname="argument allocated_storage", value=allocated_storage, expected_type=type_hints["allocated_storage"])
            check_type(argname="argument allow_major_version_upgrade", value=allow_major_version_upgrade, expected_type=type_hints["allow_major_version_upgrade"])
            check_type(argname="argument backup_retention", value=backup_retention, expected_type=type_hints["backup_retention"])
            check_type(argname="argument cloudwatch_logs_exports", value=cloudwatch_logs_exports, expected_type=type_hints["cloudwatch_logs_exports"])
            check_type(argname="argument cloudwatch_logs_retention", value=cloudwatch_logs_retention, expected_type=type_hints["cloudwatch_logs_retention"])
            check_type(argname="argument credentials_secret_name", value=credentials_secret_name, expected_type=type_hints["credentials_secret_name"])
            check_type(argname="argument credentials_username", value=credentials_username, expected_type=type_hints["credentials_username"])
            check_type(argname="argument database_name", value=database_name, expected_type=type_hints["database_name"])
            check_type(argname="argument enable_performance_insights", value=enable_performance_insights, expected_type=type_hints["enable_performance_insights"])
            check_type(argname="argument instance_identifier", value=instance_identifier, expected_type=type_hints["instance_identifier"])
            check_type(argname="argument instance_type", value=instance_type, expected_type=type_hints["instance_type"])
            check_type(argname="argument max_allocated_storage", value=max_allocated_storage, expected_type=type_hints["max_allocated_storage"])
            check_type(argname="argument multi_az", value=multi_az, expected_type=type_hints["multi_az"])
            check_type(argname="argument parameters", value=parameters, expected_type=type_hints["parameters"])
            check_type(argname="argument removal_policy", value=removal_policy, expected_type=type_hints["removal_policy"])
            check_type(argname="argument security_group_name", value=security_group_name, expected_type=type_hints["security_group_name"])
            check_type(argname="argument storage_type", value=storage_type, expected_type=type_hints["storage_type"])
            check_type(argname="argument analytics_reporting", value=analytics_reporting, expected_type=type_hints["analytics_reporting"])
            check_type(argname="argument cross_region_references", value=cross_region_references, expected_type=type_hints["cross_region_references"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument env", value=env, expected_type=type_hints["env"])
            check_type(argname="argument permissions_boundary", value=permissions_boundary, expected_type=type_hints["permissions_boundary"])
            check_type(argname="argument stack_name", value=stack_name, expected_type=type_hints["stack_name"])
            check_type(argname="argument suppress_template_indentation", value=suppress_template_indentation, expected_type=type_hints["suppress_template_indentation"])
            check_type(argname="argument synthesizer", value=synthesizer, expected_type=type_hints["synthesizer"])
            check_type(argname="argument tags", value=tags, expected_type=type_hints["tags"])
            check_type(argname="argument termination_protection", value=termination_protection, expected_type=type_hints["termination_protection"])
            check_type(argname="argument monitoring", value=monitoring, expected_type=type_hints["monitoring"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "engine": engine,
            "networking": networking,
        }
        if allocated_storage is not None:
            self._values["allocated_storage"] = allocated_storage
        if allow_major_version_upgrade is not None:
            self._values["allow_major_version_upgrade"] = allow_major_version_upgrade
        if backup_retention is not None:
            self._values["backup_retention"] = backup_retention
        if cloudwatch_logs_exports is not None:
            self._values["cloudwatch_logs_exports"] = cloudwatch_logs_exports
        if cloudwatch_logs_retention is not None:
            self._values["cloudwatch_logs_retention"] = cloudwatch_logs_retention
        if credentials_secret_name is not None:
            self._values["credentials_secret_name"] = credentials_secret_name
        if credentials_username is not None:
            self._values["credentials_username"] = credentials_username
        if database_name is not None:
            self._values["database_name"] = database_name
        if enable_performance_insights is not None:
            self._values["enable_performance_insights"] = enable_performance_insights
        if instance_identifier is not None:
            self._values["instance_identifier"] = instance_identifier
        if instance_type is not None:
            self._values["instance_type"] = instance_type
        if max_allocated_storage is not None:
            self._values["max_allocated_storage"] = max_allocated_storage
        if multi_az is not None:
            self._values["multi_az"] = multi_az
        if parameters is not None:
            self._values["parameters"] = parameters
        if removal_policy is not None:
            self._values["removal_policy"] = removal_policy
        if security_group_name is not None:
            self._values["security_group_name"] = security_group_name
        if storage_type is not None:
            self._values["storage_type"] = storage_type
        if analytics_reporting is not None:
            self._values["analytics_reporting"] = analytics_reporting
        if cross_region_references is not None:
            self._values["cross_region_references"] = cross_region_references
        if description is not None:
            self._values["description"] = description
        if env is not None:
            self._values["env"] = env
        if permissions_boundary is not None:
            self._values["permissions_boundary"] = permissions_boundary
        if stack_name is not None:
            self._values["stack_name"] = stack_name
        if suppress_template_indentation is not None:
            self._values["suppress_template_indentation"] = suppress_template_indentation
        if synthesizer is not None:
            self._values["synthesizer"] = synthesizer
        if tags is not None:
            self._values["tags"] = tags
        if termination_protection is not None:
            self._values["termination_protection"] = termination_protection
        if monitoring is not None:
            self._values["monitoring"] = monitoring

    @builtins.property
    def engine(self) -> _aws_cdk_aws_rds_ceddda9d.IInstanceEngine:
        '''(experimental) The engine of the database instance.

        :stability: experimental
        '''
        result = self._values.get("engine")
        assert result is not None, "Required property 'engine' is missing"
        return typing.cast(_aws_cdk_aws_rds_ceddda9d.IInstanceEngine, result)

    @builtins.property
    def networking(self) -> "INetworking":
        '''(experimental) The networking configuration for the database instance.

        :stability: experimental
        '''
        result = self._values.get("networking")
        assert result is not None, "Required property 'networking' is missing"
        return typing.cast("INetworking", result)

    @builtins.property
    def allocated_storage(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The allocated storage of the database instance.

        :default: 20

        :stability: experimental
        '''
        result = self._values.get("allocated_storage")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def allow_major_version_upgrade(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Whether to allow major version upgrades.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("allow_major_version_upgrade")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def backup_retention(self) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        '''(experimental) The backup retention period.

        :default: - It uses the default applied by [rds.DatabaseInstanceProps#backupRetention]https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_rds.DatabaseInstanceProps.html#backupretention).

        :stability: experimental
        '''
        result = self._values.get("backup_retention")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], result)

    @builtins.property
    def cloudwatch_logs_exports(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) The list of log types that need to be enabled for exporting to CloudWatch Logs.

        :default: - No log types are enabled.

        :stability: experimental
        '''
        result = self._values.get("cloudwatch_logs_exports")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def cloudwatch_logs_retention(
        self,
    ) -> typing.Optional[_aws_cdk_aws_logs_ceddda9d.RetentionDays]:
        '''(experimental) The number of days log events are kept in CloudWatch Logs.

        When updating this property, unsetting it doesn't remove the log retention policy. To remove the retention policy, set the value to Infinity.

        :default: logs never expire

        :stability: experimental
        '''
        result = self._values.get("cloudwatch_logs_retention")
        return typing.cast(typing.Optional[_aws_cdk_aws_logs_ceddda9d.RetentionDays], result)

    @builtins.property
    def credentials_secret_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of the secret that stores the credentials of the database.

        :default: ``${construct.node.path}/secret``

        :stability: experimental
        '''
        result = self._values.get("credentials_secret_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def credentials_username(self) -> typing.Optional[builtins.str]:
        '''(experimental) The username of the database.

        :default: db_user

        :stability: experimental
        '''
        result = self._values.get("credentials_username")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def database_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of the database.

        :default: - No default database is created.

        :stability: experimental
        '''
        result = self._values.get("database_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def enable_performance_insights(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Whether to enable Performance Insights.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("enable_performance_insights")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def instance_identifier(self) -> typing.Optional[builtins.str]:
        '''(experimental) The identifier of the database instance.

        :default: - No identifier is specified.

        :stability: experimental
        '''
        result = self._values.get("instance_identifier")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def instance_type(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.InstanceType]:
        '''(experimental) The instance type of the database instance.

        :default: - db.t3.small.

        :stability: experimental
        '''
        result = self._values.get("instance_type")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.InstanceType], result)

    @builtins.property
    def max_allocated_storage(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The maximum allocated storage of the database instance.

        :default: - No maximum allocated storage is specified.

        :stability: experimental
        '''
        result = self._values.get("max_allocated_storage")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def multi_az(self) -> typing.Optional[builtins.bool]:
        '''(experimental) If the database instance is multi-AZ.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("multi_az")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def parameters(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''(experimental) The parameters to override in the parameter group.

        :default: - No parameter is overridden.

        :stability: experimental
        '''
        result = self._values.get("parameters")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def removal_policy(self) -> typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy]:
        '''(experimental) The removal policy to apply when the cluster is removed.

        :default: RemovalPolicy.RETAIN

        :stability: experimental
        '''
        result = self._values.get("removal_policy")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy], result)

    @builtins.property
    def security_group_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of the security group.

        :default: - ``${construct.node.path}-sg``.

        :stability: experimental
        '''
        result = self._values.get("security_group_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def storage_type(self) -> typing.Optional[_aws_cdk_aws_rds_ceddda9d.StorageType]:
        '''(experimental) The storage type of the database instance.

        :default: rds.StorageType.GP3

        :stability: experimental
        '''
        result = self._values.get("storage_type")
        return typing.cast(typing.Optional[_aws_cdk_aws_rds_ceddda9d.StorageType], result)

    @builtins.property
    def analytics_reporting(self) -> typing.Optional[builtins.bool]:
        '''Include runtime versioning information in this Stack.

        :default:

        ``analyticsReporting`` setting of containing ``App``, or value of
        'aws:cdk:version-reporting' context key
        '''
        result = self._values.get("analytics_reporting")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def cross_region_references(self) -> typing.Optional[builtins.bool]:
        '''Enable this flag to allow native cross region stack references.

        Enabling this will create a CloudFormation custom resource
        in both the producing stack and consuming stack in order to perform the export/import

        This feature is currently experimental

        :default: false
        '''
        result = self._values.get("cross_region_references")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''A description of the stack.

        :default: - No description.
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def env(self) -> typing.Optional[_aws_cdk_ceddda9d.Environment]:
        '''The AWS environment (account/region) where this stack will be deployed.

        Set the ``region``/``account`` fields of ``env`` to either a concrete value to
        select the indicated environment (recommended for production stacks), or to
        the values of environment variables
        ``CDK_DEFAULT_REGION``/``CDK_DEFAULT_ACCOUNT`` to let the target environment
        depend on the AWS credentials/configuration that the CDK CLI is executed
        under (recommended for development stacks).

        If the ``Stack`` is instantiated inside a ``Stage``, any undefined
        ``region``/``account`` fields from ``env`` will default to the same field on the
        encompassing ``Stage``, if configured there.

        If either ``region`` or ``account`` are not set nor inherited from ``Stage``, the
        Stack will be considered "*environment-agnostic*"". Environment-agnostic
        stacks can be deployed to any environment but may not be able to take
        advantage of all features of the CDK. For example, they will not be able to
        use environmental context lookups such as ``ec2.Vpc.fromLookup`` and will not
        automatically translate Service Principals to the right format based on the
        environment's AWS partition, and other such enhancements.

        :default:

        - The environment of the containing ``Stage`` if available,
        otherwise create the stack will be environment-agnostic.

        Example::

            // Use a concrete account and region to deploy this stack to:
            // `.account` and `.region` will simply return these values.
            new Stack(app, 'Stack1', {
              env: {
                account: '123456789012',
                region: 'us-east-1'
              },
            });
            
            // Use the CLI's current credentials to determine the target environment:
            // `.account` and `.region` will reflect the account+region the CLI
            // is configured to use (based on the user CLI credentials)
            new Stack(app, 'Stack2', {
              env: {
                account: process.env.CDK_DEFAULT_ACCOUNT,
                region: process.env.CDK_DEFAULT_REGION
              },
            });
            
            // Define multiple stacks stage associated with an environment
            const myStage = new Stage(app, 'MyStage', {
              env: {
                account: '123456789012',
                region: 'us-east-1'
              }
            });
            
            // both of these stacks will use the stage's account/region:
            // `.account` and `.region` will resolve to the concrete values as above
            new MyStack(myStage, 'Stack1');
            new YourStack(myStage, 'Stack2');
            
            // Define an environment-agnostic stack:
            // `.account` and `.region` will resolve to `{ "Ref": "AWS::AccountId" }` and `{ "Ref": "AWS::Region" }` respectively.
            // which will only resolve to actual values by CloudFormation during deployment.
            new MyStack(app, 'Stack1');
        '''
        result = self._values.get("env")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Environment], result)

    @builtins.property
    def permissions_boundary(
        self,
    ) -> typing.Optional[_aws_cdk_ceddda9d.PermissionsBoundary]:
        '''Options for applying a permissions boundary to all IAM Roles and Users created within this Stage.

        :default: - no permissions boundary is applied
        '''
        result = self._values.get("permissions_boundary")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.PermissionsBoundary], result)

    @builtins.property
    def stack_name(self) -> typing.Optional[builtins.str]:
        '''Name to deploy the stack with.

        :default: - Derived from construct path.
        '''
        result = self._values.get("stack_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def suppress_template_indentation(self) -> typing.Optional[builtins.bool]:
        '''Enable this flag to suppress indentation in generated CloudFormation templates.

        If not specified, the value of the ``@aws-cdk/core:suppressTemplateIndentation``
        context key will be used. If that is not specified, then the
        default value ``false`` will be used.

        :default: - the value of ``@aws-cdk/core:suppressTemplateIndentation``, or ``false`` if that is not set.
        '''
        result = self._values.get("suppress_template_indentation")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def synthesizer(self) -> typing.Optional[_aws_cdk_ceddda9d.IStackSynthesizer]:
        '''Synthesis method to use while deploying this stack.

        The Stack Synthesizer controls aspects of synthesis and deployment,
        like how assets are referenced and what IAM roles to use. For more
        information, see the README of the main CDK package.

        If not specified, the ``defaultStackSynthesizer`` from ``App`` will be used.
        If that is not specified, ``DefaultStackSynthesizer`` is used if
        ``@aws-cdk/core:newStyleStackSynthesis`` is set to ``true`` or the CDK major
        version is v2. In CDK v1 ``LegacyStackSynthesizer`` is the default if no
        other synthesizer is specified.

        :default: - The synthesizer specified on ``App``, or ``DefaultStackSynthesizer`` otherwise.
        '''
        result = self._values.get("synthesizer")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.IStackSynthesizer], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Stack tags that will be applied to all the taggable resources and the stack itself.

        :default: {}
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def termination_protection(self) -> typing.Optional[builtins.bool]:
        '''Whether to enable termination protection for this stack.

        :default: false
        '''
        result = self._values.get("termination_protection")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def monitoring(self) -> typing.Optional["MonitoringFacadeProps"]:
        '''(experimental) The monitoring configuration to apply to this stack.

        :default: - No monitoring.

        :stability: experimental
        '''
        result = self._values.get("monitoring")
        return typing.cast(typing.Optional["MonitoringFacadeProps"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DatabaseInstanceStackProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@condensetech/cdk-constructs.EntrypointCertificateProps",
    jsii_struct_bases=[],
    name_mapping={
        "certificate": "certificate",
        "certificate_arn": "certificateArn",
        "wildcard_certificate": "wildcardCertificate",
    },
)
class EntrypointCertificateProps:
    def __init__(
        self,
        *,
        certificate: typing.Optional[_aws_cdk_aws_certificatemanager_ceddda9d.ICertificate] = None,
        certificate_arn: typing.Optional[builtins.str] = None,
        wildcard_certificate: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param certificate: (experimental) The certificate to use. Default: - A new certificate is created through ACM
        :param certificate_arn: (experimental) The ARN of the existing certificate to use. Default: - A new certificate is created through ACM.
        :param wildcard_certificate: (experimental) Indicates whether the HTTPS certificate should be bound to all subdomains. Default: true

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e5e0795d189370067efff1cf7b82e81499224af835fb61b6505603886fd34217)
            check_type(argname="argument certificate", value=certificate, expected_type=type_hints["certificate"])
            check_type(argname="argument certificate_arn", value=certificate_arn, expected_type=type_hints["certificate_arn"])
            check_type(argname="argument wildcard_certificate", value=wildcard_certificate, expected_type=type_hints["wildcard_certificate"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if certificate is not None:
            self._values["certificate"] = certificate
        if certificate_arn is not None:
            self._values["certificate_arn"] = certificate_arn
        if wildcard_certificate is not None:
            self._values["wildcard_certificate"] = wildcard_certificate

    @builtins.property
    def certificate(
        self,
    ) -> typing.Optional[_aws_cdk_aws_certificatemanager_ceddda9d.ICertificate]:
        '''(experimental) The certificate to use.

        :default: - A new certificate is created through ACM

        :stability: experimental
        '''
        result = self._values.get("certificate")
        return typing.cast(typing.Optional[_aws_cdk_aws_certificatemanager_ceddda9d.ICertificate], result)

    @builtins.property
    def certificate_arn(self) -> typing.Optional[builtins.str]:
        '''(experimental) The ARN of the existing certificate to use.

        :default: - A new certificate is created through ACM.

        :stability: experimental
        '''
        result = self._values.get("certificate_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def wildcard_certificate(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Indicates whether the HTTPS certificate should be bound to all subdomains.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("wildcard_certificate")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "EntrypointCertificateProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@condensetech/cdk-constructs.EntrypointFromAttributes",
    jsii_struct_bases=[],
    name_mapping={
        "listener_arn": "listenerArn",
        "load_balancer_arn": "loadBalancerArn",
        "security_group_id": "securityGroupId",
        "domain_name": "domainName",
        "entrypoint_name": "entrypointName",
        "priority_allocator_service_token": "priorityAllocatorServiceToken",
    },
)
class EntrypointFromAttributes:
    def __init__(
        self,
        *,
        listener_arn: builtins.str,
        load_balancer_arn: builtins.str,
        security_group_id: builtins.str,
        domain_name: typing.Optional[builtins.str] = None,
        entrypoint_name: typing.Optional[builtins.str] = None,
        priority_allocator_service_token: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param listener_arn: (experimental) ARN of the load balancer HTTPS listener.
        :param load_balancer_arn: (experimental) The load balancer ARN.
        :param security_group_id: (experimental) The security group ID of the load balancer.
        :param domain_name: (experimental) The load balancer custom domain name. Default: - No domain name is specified, and the load balancer dns name will be used.
        :param entrypoint_name: (experimental) The entrypoint name to use for referencing the priority allocator.
        :param priority_allocator_service_token: (experimental) The Priority Allocator service token to use for referencing the priority allocator.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8c3bfc299e27a3860e607664a4c27cda4af08536297db566a2b2aedc708f3b8b)
            check_type(argname="argument listener_arn", value=listener_arn, expected_type=type_hints["listener_arn"])
            check_type(argname="argument load_balancer_arn", value=load_balancer_arn, expected_type=type_hints["load_balancer_arn"])
            check_type(argname="argument security_group_id", value=security_group_id, expected_type=type_hints["security_group_id"])
            check_type(argname="argument domain_name", value=domain_name, expected_type=type_hints["domain_name"])
            check_type(argname="argument entrypoint_name", value=entrypoint_name, expected_type=type_hints["entrypoint_name"])
            check_type(argname="argument priority_allocator_service_token", value=priority_allocator_service_token, expected_type=type_hints["priority_allocator_service_token"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "listener_arn": listener_arn,
            "load_balancer_arn": load_balancer_arn,
            "security_group_id": security_group_id,
        }
        if domain_name is not None:
            self._values["domain_name"] = domain_name
        if entrypoint_name is not None:
            self._values["entrypoint_name"] = entrypoint_name
        if priority_allocator_service_token is not None:
            self._values["priority_allocator_service_token"] = priority_allocator_service_token

    @builtins.property
    def listener_arn(self) -> builtins.str:
        '''(experimental) ARN of the load balancer HTTPS listener.

        :stability: experimental
        '''
        result = self._values.get("listener_arn")
        assert result is not None, "Required property 'listener_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def load_balancer_arn(self) -> builtins.str:
        '''(experimental) The load balancer ARN.

        :stability: experimental
        '''
        result = self._values.get("load_balancer_arn")
        assert result is not None, "Required property 'load_balancer_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def security_group_id(self) -> builtins.str:
        '''(experimental) The security group ID of the load balancer.

        :stability: experimental
        '''
        result = self._values.get("security_group_id")
        assert result is not None, "Required property 'security_group_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def domain_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) The load balancer custom domain name.

        :default: - No domain name is specified, and the load balancer dns name will be used.

        :stability: experimental
        '''
        result = self._values.get("domain_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def entrypoint_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) The entrypoint name to use for referencing the priority allocator.

        :stability: experimental
        '''
        result = self._values.get("entrypoint_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def priority_allocator_service_token(self) -> typing.Optional[builtins.str]:
        '''(experimental) The Priority Allocator service token to use for referencing the priority allocator.

        :stability: experimental
        '''
        result = self._values.get("priority_allocator_service_token")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "EntrypointFromAttributes(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@condensetech/cdk-constructs.EntrypointFromLookupProps",
    jsii_struct_bases=[],
    name_mapping={
        "entrypoint_name": "entrypointName",
        "domain_name": "domainName",
        "vpc": "vpc",
        "vpc_lookup": "vpcLookup",
    },
)
class EntrypointFromLookupProps:
    def __init__(
        self,
        *,
        entrypoint_name: builtins.str,
        domain_name: typing.Optional[builtins.str] = None,
        vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
        vpc_lookup: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.VpcLookupOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param entrypoint_name: (experimental) The entrypoint name to lookup.
        :param domain_name: (experimental) The load balancer custom domain name. Default: - No domain name is specified, and the load balancer dns name will be used.
        :param vpc: (experimental) The VPC where the entrypoint is located. Required if vpcLookup is not provided.
        :param vpc_lookup: (experimental) The VPC lookup options to find the VPC where the entrypoint is located. Required if vpc is not provided.

        :stability: experimental
        '''
        if isinstance(vpc_lookup, dict):
            vpc_lookup = _aws_cdk_aws_ec2_ceddda9d.VpcLookupOptions(**vpc_lookup)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6d6cd06c158bbf007dcd6d881c99b7e87d281495cface2615f9a39294352c91f)
            check_type(argname="argument entrypoint_name", value=entrypoint_name, expected_type=type_hints["entrypoint_name"])
            check_type(argname="argument domain_name", value=domain_name, expected_type=type_hints["domain_name"])
            check_type(argname="argument vpc", value=vpc, expected_type=type_hints["vpc"])
            check_type(argname="argument vpc_lookup", value=vpc_lookup, expected_type=type_hints["vpc_lookup"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "entrypoint_name": entrypoint_name,
        }
        if domain_name is not None:
            self._values["domain_name"] = domain_name
        if vpc is not None:
            self._values["vpc"] = vpc
        if vpc_lookup is not None:
            self._values["vpc_lookup"] = vpc_lookup

    @builtins.property
    def entrypoint_name(self) -> builtins.str:
        '''(experimental) The entrypoint name to lookup.

        :stability: experimental
        '''
        result = self._values.get("entrypoint_name")
        assert result is not None, "Required property 'entrypoint_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def domain_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) The load balancer custom domain name.

        :default: - No domain name is specified, and the load balancer dns name will be used.

        :stability: experimental
        '''
        result = self._values.get("domain_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def vpc(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc]:
        '''(experimental) The VPC where the entrypoint is located.

        Required if vpcLookup is not provided.

        :stability: experimental
        '''
        result = self._values.get("vpc")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc], result)

    @builtins.property
    def vpc_lookup(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.VpcLookupOptions]:
        '''(experimental) The VPC lookup options to find the VPC where the entrypoint is located.

        Required if vpc is not provided.

        :stability: experimental
        '''
        result = self._values.get("vpc_lookup")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.VpcLookupOptions], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "EntrypointFromLookupProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@condensetech/cdk-constructs.EntrypointProps",
    jsii_struct_bases=[],
    name_mapping={
        "domain_name": "domainName",
        "networking": "networking",
        "certificate": "certificate",
        "certificates": "certificates",
        "entrypoint_name": "entrypointName",
        "entrypoint_security_group_name": "entrypointSecurityGroupName",
        "hosted_zone_props": "hostedZoneProps",
        "logs_bucket": "logsBucket",
        "priority_allocator": "priorityAllocator",
        "security_group_name": "securityGroupName",
    },
)
class EntrypointProps:
    def __init__(
        self,
        *,
        domain_name: builtins.str,
        networking: "INetworking",
        certificate: typing.Optional[typing.Union[EntrypointCertificateProps, typing.Dict[builtins.str, typing.Any]]] = None,
        certificates: typing.Optional[typing.Sequence[typing.Union[EntrypointCertificateProps, typing.Dict[builtins.str, typing.Any]]]] = None,
        entrypoint_name: typing.Optional[builtins.str] = None,
        entrypoint_security_group_name: typing.Optional[builtins.str] = None,
        hosted_zone_props: typing.Optional[typing.Union[_aws_cdk_aws_route53_ceddda9d.HostedZoneAttributes, typing.Dict[builtins.str, typing.Any]]] = None,
        logs_bucket: typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket] = None,
        priority_allocator: typing.Optional[typing.Union[ApplicationListenerPriorityAllocatorConfig, typing.Dict[builtins.str, typing.Any]]] = None,
        security_group_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Properties for the Entrypoint construct.

        :param domain_name: (experimental) The domain name to which the entrypoint is associated.
        :param networking: (experimental) The networking configuration for the entrypoint.
        :param certificate: (deprecated) Certificate properties for the entrypoint. Default: - A new certificate is created through ACM, bound to domainName, *.domainName.
        :param certificates: (experimental) Certificate properties for the entrypoint. Default: - A new certificate is created through ACM, bound to domainName, *.domainName.
        :param entrypoint_name: (experimental) The name of the entrypoint. This value is used as the name of the underlying Application Load Balancer (ALB) and as the prefix for the name of the associated security group. Default: - No name is specified.
        :param entrypoint_security_group_name: (deprecated) The name of the security group for the entrypoint. Default: ``${entrypointName}-sg``
        :param hosted_zone_props: (experimental) The Route 53 hosted zone attributes for the domain name.
        :param logs_bucket: (experimental) The S3 bucket to store the logs of the ALB. Setting this will enable the access logs for the ALB. Default: - Logging is disabled.
        :param priority_allocator: (experimental) Customize the priority allocator for the entrypoint.
        :param security_group_name: (experimental) The name of the security group for the entrypoint. Default: ``${entrypointName}-sg`` if ``entrypointName`` is specified, otherwise no name is specified.

        :stability: experimental
        '''
        if isinstance(certificate, dict):
            certificate = EntrypointCertificateProps(**certificate)
        if isinstance(hosted_zone_props, dict):
            hosted_zone_props = _aws_cdk_aws_route53_ceddda9d.HostedZoneAttributes(**hosted_zone_props)
        if isinstance(priority_allocator, dict):
            priority_allocator = ApplicationListenerPriorityAllocatorConfig(**priority_allocator)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__83a61ef01fb98c7353c39945cc7c3dcb1c823185ce1714ad3ca8e84636eaec89)
            check_type(argname="argument domain_name", value=domain_name, expected_type=type_hints["domain_name"])
            check_type(argname="argument networking", value=networking, expected_type=type_hints["networking"])
            check_type(argname="argument certificate", value=certificate, expected_type=type_hints["certificate"])
            check_type(argname="argument certificates", value=certificates, expected_type=type_hints["certificates"])
            check_type(argname="argument entrypoint_name", value=entrypoint_name, expected_type=type_hints["entrypoint_name"])
            check_type(argname="argument entrypoint_security_group_name", value=entrypoint_security_group_name, expected_type=type_hints["entrypoint_security_group_name"])
            check_type(argname="argument hosted_zone_props", value=hosted_zone_props, expected_type=type_hints["hosted_zone_props"])
            check_type(argname="argument logs_bucket", value=logs_bucket, expected_type=type_hints["logs_bucket"])
            check_type(argname="argument priority_allocator", value=priority_allocator, expected_type=type_hints["priority_allocator"])
            check_type(argname="argument security_group_name", value=security_group_name, expected_type=type_hints["security_group_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "domain_name": domain_name,
            "networking": networking,
        }
        if certificate is not None:
            self._values["certificate"] = certificate
        if certificates is not None:
            self._values["certificates"] = certificates
        if entrypoint_name is not None:
            self._values["entrypoint_name"] = entrypoint_name
        if entrypoint_security_group_name is not None:
            self._values["entrypoint_security_group_name"] = entrypoint_security_group_name
        if hosted_zone_props is not None:
            self._values["hosted_zone_props"] = hosted_zone_props
        if logs_bucket is not None:
            self._values["logs_bucket"] = logs_bucket
        if priority_allocator is not None:
            self._values["priority_allocator"] = priority_allocator
        if security_group_name is not None:
            self._values["security_group_name"] = security_group_name

    @builtins.property
    def domain_name(self) -> builtins.str:
        '''(experimental) The domain name to which the entrypoint is associated.

        :stability: experimental
        '''
        result = self._values.get("domain_name")
        assert result is not None, "Required property 'domain_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def networking(self) -> "INetworking":
        '''(experimental) The networking configuration for the entrypoint.

        :stability: experimental
        '''
        result = self._values.get("networking")
        assert result is not None, "Required property 'networking' is missing"
        return typing.cast("INetworking", result)

    @builtins.property
    def certificate(self) -> typing.Optional[EntrypointCertificateProps]:
        '''(deprecated) Certificate properties for the entrypoint.

        :default: - A new certificate is created through ACM, bound to domainName, *.domainName.

        :deprecated: Use ``certificates`` instead.

        :stability: deprecated
        '''
        result = self._values.get("certificate")
        return typing.cast(typing.Optional[EntrypointCertificateProps], result)

    @builtins.property
    def certificates(self) -> typing.Optional[typing.List[EntrypointCertificateProps]]:
        '''(experimental) Certificate properties for the entrypoint.

        :default: - A new certificate is created through ACM, bound to domainName, *.domainName.

        :stability: experimental
        '''
        result = self._values.get("certificates")
        return typing.cast(typing.Optional[typing.List[EntrypointCertificateProps]], result)

    @builtins.property
    def entrypoint_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of the entrypoint.

        This value is used as the name of the underlying Application Load Balancer (ALB)
        and as the prefix for the name of the associated security group.

        :default: - No name is specified.

        :stability: experimental
        '''
        result = self._values.get("entrypoint_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def entrypoint_security_group_name(self) -> typing.Optional[builtins.str]:
        '''(deprecated) The name of the security group for the entrypoint.

        :default: ``${entrypointName}-sg``

        :deprecated: Use ``securityGroupName`` instead.

        :stability: deprecated
        '''
        result = self._values.get("entrypoint_security_group_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def hosted_zone_props(
        self,
    ) -> typing.Optional[_aws_cdk_aws_route53_ceddda9d.HostedZoneAttributes]:
        '''(experimental) The Route 53 hosted zone attributes for the domain name.

        :stability: experimental
        '''
        result = self._values.get("hosted_zone_props")
        return typing.cast(typing.Optional[_aws_cdk_aws_route53_ceddda9d.HostedZoneAttributes], result)

    @builtins.property
    def logs_bucket(self) -> typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket]:
        '''(experimental) The S3 bucket to store the logs of the ALB.

        Setting this will enable the access logs for the ALB.

        :default: - Logging is disabled.

        :stability: experimental
        '''
        result = self._values.get("logs_bucket")
        return typing.cast(typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket], result)

    @builtins.property
    def priority_allocator(
        self,
    ) -> typing.Optional[ApplicationListenerPriorityAllocatorConfig]:
        '''(experimental) Customize the priority allocator for the entrypoint.

        :stability: experimental
        '''
        result = self._values.get("priority_allocator")
        return typing.cast(typing.Optional[ApplicationListenerPriorityAllocatorConfig], result)

    @builtins.property
    def security_group_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of the security group for the entrypoint.

        :default: ``${entrypointName}-sg`` if ``entrypointName`` is specified, otherwise no name is specified.

        :stability: experimental
        '''
        result = self._values.get("security_group_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "EntrypointProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@condensetech/cdk-constructs.EntrypointStackProps",
    jsii_struct_bases=[EntrypointProps, _aws_cdk_ceddda9d.StackProps],
    name_mapping={
        "domain_name": "domainName",
        "networking": "networking",
        "certificate": "certificate",
        "certificates": "certificates",
        "entrypoint_name": "entrypointName",
        "entrypoint_security_group_name": "entrypointSecurityGroupName",
        "hosted_zone_props": "hostedZoneProps",
        "logs_bucket": "logsBucket",
        "priority_allocator": "priorityAllocator",
        "security_group_name": "securityGroupName",
        "analytics_reporting": "analyticsReporting",
        "cross_region_references": "crossRegionReferences",
        "description": "description",
        "env": "env",
        "permissions_boundary": "permissionsBoundary",
        "stack_name": "stackName",
        "suppress_template_indentation": "suppressTemplateIndentation",
        "synthesizer": "synthesizer",
        "tags": "tags",
        "termination_protection": "terminationProtection",
        "monitoring": "monitoring",
    },
)
class EntrypointStackProps(EntrypointProps, _aws_cdk_ceddda9d.StackProps):
    def __init__(
        self,
        *,
        domain_name: builtins.str,
        networking: "INetworking",
        certificate: typing.Optional[typing.Union[EntrypointCertificateProps, typing.Dict[builtins.str, typing.Any]]] = None,
        certificates: typing.Optional[typing.Sequence[typing.Union[EntrypointCertificateProps, typing.Dict[builtins.str, typing.Any]]]] = None,
        entrypoint_name: typing.Optional[builtins.str] = None,
        entrypoint_security_group_name: typing.Optional[builtins.str] = None,
        hosted_zone_props: typing.Optional[typing.Union[_aws_cdk_aws_route53_ceddda9d.HostedZoneAttributes, typing.Dict[builtins.str, typing.Any]]] = None,
        logs_bucket: typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket] = None,
        priority_allocator: typing.Optional[typing.Union[ApplicationListenerPriorityAllocatorConfig, typing.Dict[builtins.str, typing.Any]]] = None,
        security_group_name: typing.Optional[builtins.str] = None,
        analytics_reporting: typing.Optional[builtins.bool] = None,
        cross_region_references: typing.Optional[builtins.bool] = None,
        description: typing.Optional[builtins.str] = None,
        env: typing.Optional[typing.Union[_aws_cdk_ceddda9d.Environment, typing.Dict[builtins.str, typing.Any]]] = None,
        permissions_boundary: typing.Optional[_aws_cdk_ceddda9d.PermissionsBoundary] = None,
        stack_name: typing.Optional[builtins.str] = None,
        suppress_template_indentation: typing.Optional[builtins.bool] = None,
        synthesizer: typing.Optional[_aws_cdk_ceddda9d.IStackSynthesizer] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        termination_protection: typing.Optional[builtins.bool] = None,
        monitoring: typing.Optional[typing.Union["MonitoringFacadeProps", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''(experimental) Properties for the EntrypointStack.

        :param domain_name: (experimental) The domain name to which the entrypoint is associated.
        :param networking: (experimental) The networking configuration for the entrypoint.
        :param certificate: (deprecated) Certificate properties for the entrypoint. Default: - A new certificate is created through ACM, bound to domainName, *.domainName.
        :param certificates: (experimental) Certificate properties for the entrypoint. Default: - A new certificate is created through ACM, bound to domainName, *.domainName.
        :param entrypoint_name: (experimental) The name of the entrypoint. This value is used as the name of the underlying Application Load Balancer (ALB) and as the prefix for the name of the associated security group. Default: - No name is specified.
        :param entrypoint_security_group_name: (deprecated) The name of the security group for the entrypoint. Default: ``${entrypointName}-sg``
        :param hosted_zone_props: (experimental) The Route 53 hosted zone attributes for the domain name.
        :param logs_bucket: (experimental) The S3 bucket to store the logs of the ALB. Setting this will enable the access logs for the ALB. Default: - Logging is disabled.
        :param priority_allocator: (experimental) Customize the priority allocator for the entrypoint.
        :param security_group_name: (experimental) The name of the security group for the entrypoint. Default: ``${entrypointName}-sg`` if ``entrypointName`` is specified, otherwise no name is specified.
        :param analytics_reporting: Include runtime versioning information in this Stack. Default: ``analyticsReporting`` setting of containing ``App``, or value of 'aws:cdk:version-reporting' context key
        :param cross_region_references: Enable this flag to allow native cross region stack references. Enabling this will create a CloudFormation custom resource in both the producing stack and consuming stack in order to perform the export/import This feature is currently experimental Default: false
        :param description: A description of the stack. Default: - No description.
        :param env: The AWS environment (account/region) where this stack will be deployed. Set the ``region``/``account`` fields of ``env`` to either a concrete value to select the indicated environment (recommended for production stacks), or to the values of environment variables ``CDK_DEFAULT_REGION``/``CDK_DEFAULT_ACCOUNT`` to let the target environment depend on the AWS credentials/configuration that the CDK CLI is executed under (recommended for development stacks). If the ``Stack`` is instantiated inside a ``Stage``, any undefined ``region``/``account`` fields from ``env`` will default to the same field on the encompassing ``Stage``, if configured there. If either ``region`` or ``account`` are not set nor inherited from ``Stage``, the Stack will be considered "*environment-agnostic*"". Environment-agnostic stacks can be deployed to any environment but may not be able to take advantage of all features of the CDK. For example, they will not be able to use environmental context lookups such as ``ec2.Vpc.fromLookup`` and will not automatically translate Service Principals to the right format based on the environment's AWS partition, and other such enhancements. Default: - The environment of the containing ``Stage`` if available, otherwise create the stack will be environment-agnostic.
        :param permissions_boundary: Options for applying a permissions boundary to all IAM Roles and Users created within this Stage. Default: - no permissions boundary is applied
        :param stack_name: Name to deploy the stack with. Default: - Derived from construct path.
        :param suppress_template_indentation: Enable this flag to suppress indentation in generated CloudFormation templates. If not specified, the value of the ``@aws-cdk/core:suppressTemplateIndentation`` context key will be used. If that is not specified, then the default value ``false`` will be used. Default: - the value of ``@aws-cdk/core:suppressTemplateIndentation``, or ``false`` if that is not set.
        :param synthesizer: Synthesis method to use while deploying this stack. The Stack Synthesizer controls aspects of synthesis and deployment, like how assets are referenced and what IAM roles to use. For more information, see the README of the main CDK package. If not specified, the ``defaultStackSynthesizer`` from ``App`` will be used. If that is not specified, ``DefaultStackSynthesizer`` is used if ``@aws-cdk/core:newStyleStackSynthesis`` is set to ``true`` or the CDK major version is v2. In CDK v1 ``LegacyStackSynthesizer`` is the default if no other synthesizer is specified. Default: - The synthesizer specified on ``App``, or ``DefaultStackSynthesizer`` otherwise.
        :param tags: Stack tags that will be applied to all the taggable resources and the stack itself. Default: {}
        :param termination_protection: Whether to enable termination protection for this stack. Default: false
        :param monitoring: (experimental) The monitoring configuration to apply to this stack. Default: - No monitoring.

        :stability: experimental
        '''
        if isinstance(certificate, dict):
            certificate = EntrypointCertificateProps(**certificate)
        if isinstance(hosted_zone_props, dict):
            hosted_zone_props = _aws_cdk_aws_route53_ceddda9d.HostedZoneAttributes(**hosted_zone_props)
        if isinstance(priority_allocator, dict):
            priority_allocator = ApplicationListenerPriorityAllocatorConfig(**priority_allocator)
        if isinstance(env, dict):
            env = _aws_cdk_ceddda9d.Environment(**env)
        if isinstance(monitoring, dict):
            monitoring = MonitoringFacadeProps(**monitoring)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c85f5510b68e3824ed823dfefbd0ed33f8c7fb08af1202ef020e1e4b69f543d0)
            check_type(argname="argument domain_name", value=domain_name, expected_type=type_hints["domain_name"])
            check_type(argname="argument networking", value=networking, expected_type=type_hints["networking"])
            check_type(argname="argument certificate", value=certificate, expected_type=type_hints["certificate"])
            check_type(argname="argument certificates", value=certificates, expected_type=type_hints["certificates"])
            check_type(argname="argument entrypoint_name", value=entrypoint_name, expected_type=type_hints["entrypoint_name"])
            check_type(argname="argument entrypoint_security_group_name", value=entrypoint_security_group_name, expected_type=type_hints["entrypoint_security_group_name"])
            check_type(argname="argument hosted_zone_props", value=hosted_zone_props, expected_type=type_hints["hosted_zone_props"])
            check_type(argname="argument logs_bucket", value=logs_bucket, expected_type=type_hints["logs_bucket"])
            check_type(argname="argument priority_allocator", value=priority_allocator, expected_type=type_hints["priority_allocator"])
            check_type(argname="argument security_group_name", value=security_group_name, expected_type=type_hints["security_group_name"])
            check_type(argname="argument analytics_reporting", value=analytics_reporting, expected_type=type_hints["analytics_reporting"])
            check_type(argname="argument cross_region_references", value=cross_region_references, expected_type=type_hints["cross_region_references"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument env", value=env, expected_type=type_hints["env"])
            check_type(argname="argument permissions_boundary", value=permissions_boundary, expected_type=type_hints["permissions_boundary"])
            check_type(argname="argument stack_name", value=stack_name, expected_type=type_hints["stack_name"])
            check_type(argname="argument suppress_template_indentation", value=suppress_template_indentation, expected_type=type_hints["suppress_template_indentation"])
            check_type(argname="argument synthesizer", value=synthesizer, expected_type=type_hints["synthesizer"])
            check_type(argname="argument tags", value=tags, expected_type=type_hints["tags"])
            check_type(argname="argument termination_protection", value=termination_protection, expected_type=type_hints["termination_protection"])
            check_type(argname="argument monitoring", value=monitoring, expected_type=type_hints["monitoring"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "domain_name": domain_name,
            "networking": networking,
        }
        if certificate is not None:
            self._values["certificate"] = certificate
        if certificates is not None:
            self._values["certificates"] = certificates
        if entrypoint_name is not None:
            self._values["entrypoint_name"] = entrypoint_name
        if entrypoint_security_group_name is not None:
            self._values["entrypoint_security_group_name"] = entrypoint_security_group_name
        if hosted_zone_props is not None:
            self._values["hosted_zone_props"] = hosted_zone_props
        if logs_bucket is not None:
            self._values["logs_bucket"] = logs_bucket
        if priority_allocator is not None:
            self._values["priority_allocator"] = priority_allocator
        if security_group_name is not None:
            self._values["security_group_name"] = security_group_name
        if analytics_reporting is not None:
            self._values["analytics_reporting"] = analytics_reporting
        if cross_region_references is not None:
            self._values["cross_region_references"] = cross_region_references
        if description is not None:
            self._values["description"] = description
        if env is not None:
            self._values["env"] = env
        if permissions_boundary is not None:
            self._values["permissions_boundary"] = permissions_boundary
        if stack_name is not None:
            self._values["stack_name"] = stack_name
        if suppress_template_indentation is not None:
            self._values["suppress_template_indentation"] = suppress_template_indentation
        if synthesizer is not None:
            self._values["synthesizer"] = synthesizer
        if tags is not None:
            self._values["tags"] = tags
        if termination_protection is not None:
            self._values["termination_protection"] = termination_protection
        if monitoring is not None:
            self._values["monitoring"] = monitoring

    @builtins.property
    def domain_name(self) -> builtins.str:
        '''(experimental) The domain name to which the entrypoint is associated.

        :stability: experimental
        '''
        result = self._values.get("domain_name")
        assert result is not None, "Required property 'domain_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def networking(self) -> "INetworking":
        '''(experimental) The networking configuration for the entrypoint.

        :stability: experimental
        '''
        result = self._values.get("networking")
        assert result is not None, "Required property 'networking' is missing"
        return typing.cast("INetworking", result)

    @builtins.property
    def certificate(self) -> typing.Optional[EntrypointCertificateProps]:
        '''(deprecated) Certificate properties for the entrypoint.

        :default: - A new certificate is created through ACM, bound to domainName, *.domainName.

        :deprecated: Use ``certificates`` instead.

        :stability: deprecated
        '''
        result = self._values.get("certificate")
        return typing.cast(typing.Optional[EntrypointCertificateProps], result)

    @builtins.property
    def certificates(self) -> typing.Optional[typing.List[EntrypointCertificateProps]]:
        '''(experimental) Certificate properties for the entrypoint.

        :default: - A new certificate is created through ACM, bound to domainName, *.domainName.

        :stability: experimental
        '''
        result = self._values.get("certificates")
        return typing.cast(typing.Optional[typing.List[EntrypointCertificateProps]], result)

    @builtins.property
    def entrypoint_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of the entrypoint.

        This value is used as the name of the underlying Application Load Balancer (ALB)
        and as the prefix for the name of the associated security group.

        :default: - No name is specified.

        :stability: experimental
        '''
        result = self._values.get("entrypoint_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def entrypoint_security_group_name(self) -> typing.Optional[builtins.str]:
        '''(deprecated) The name of the security group for the entrypoint.

        :default: ``${entrypointName}-sg``

        :deprecated: Use ``securityGroupName`` instead.

        :stability: deprecated
        '''
        result = self._values.get("entrypoint_security_group_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def hosted_zone_props(
        self,
    ) -> typing.Optional[_aws_cdk_aws_route53_ceddda9d.HostedZoneAttributes]:
        '''(experimental) The Route 53 hosted zone attributes for the domain name.

        :stability: experimental
        '''
        result = self._values.get("hosted_zone_props")
        return typing.cast(typing.Optional[_aws_cdk_aws_route53_ceddda9d.HostedZoneAttributes], result)

    @builtins.property
    def logs_bucket(self) -> typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket]:
        '''(experimental) The S3 bucket to store the logs of the ALB.

        Setting this will enable the access logs for the ALB.

        :default: - Logging is disabled.

        :stability: experimental
        '''
        result = self._values.get("logs_bucket")
        return typing.cast(typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket], result)

    @builtins.property
    def priority_allocator(
        self,
    ) -> typing.Optional[ApplicationListenerPriorityAllocatorConfig]:
        '''(experimental) Customize the priority allocator for the entrypoint.

        :stability: experimental
        '''
        result = self._values.get("priority_allocator")
        return typing.cast(typing.Optional[ApplicationListenerPriorityAllocatorConfig], result)

    @builtins.property
    def security_group_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of the security group for the entrypoint.

        :default: ``${entrypointName}-sg`` if ``entrypointName`` is specified, otherwise no name is specified.

        :stability: experimental
        '''
        result = self._values.get("security_group_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def analytics_reporting(self) -> typing.Optional[builtins.bool]:
        '''Include runtime versioning information in this Stack.

        :default:

        ``analyticsReporting`` setting of containing ``App``, or value of
        'aws:cdk:version-reporting' context key
        '''
        result = self._values.get("analytics_reporting")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def cross_region_references(self) -> typing.Optional[builtins.bool]:
        '''Enable this flag to allow native cross region stack references.

        Enabling this will create a CloudFormation custom resource
        in both the producing stack and consuming stack in order to perform the export/import

        This feature is currently experimental

        :default: false
        '''
        result = self._values.get("cross_region_references")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''A description of the stack.

        :default: - No description.
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def env(self) -> typing.Optional[_aws_cdk_ceddda9d.Environment]:
        '''The AWS environment (account/region) where this stack will be deployed.

        Set the ``region``/``account`` fields of ``env`` to either a concrete value to
        select the indicated environment (recommended for production stacks), or to
        the values of environment variables
        ``CDK_DEFAULT_REGION``/``CDK_DEFAULT_ACCOUNT`` to let the target environment
        depend on the AWS credentials/configuration that the CDK CLI is executed
        under (recommended for development stacks).

        If the ``Stack`` is instantiated inside a ``Stage``, any undefined
        ``region``/``account`` fields from ``env`` will default to the same field on the
        encompassing ``Stage``, if configured there.

        If either ``region`` or ``account`` are not set nor inherited from ``Stage``, the
        Stack will be considered "*environment-agnostic*"". Environment-agnostic
        stacks can be deployed to any environment but may not be able to take
        advantage of all features of the CDK. For example, they will not be able to
        use environmental context lookups such as ``ec2.Vpc.fromLookup`` and will not
        automatically translate Service Principals to the right format based on the
        environment's AWS partition, and other such enhancements.

        :default:

        - The environment of the containing ``Stage`` if available,
        otherwise create the stack will be environment-agnostic.

        Example::

            // Use a concrete account and region to deploy this stack to:
            // `.account` and `.region` will simply return these values.
            new Stack(app, 'Stack1', {
              env: {
                account: '123456789012',
                region: 'us-east-1'
              },
            });
            
            // Use the CLI's current credentials to determine the target environment:
            // `.account` and `.region` will reflect the account+region the CLI
            // is configured to use (based on the user CLI credentials)
            new Stack(app, 'Stack2', {
              env: {
                account: process.env.CDK_DEFAULT_ACCOUNT,
                region: process.env.CDK_DEFAULT_REGION
              },
            });
            
            // Define multiple stacks stage associated with an environment
            const myStage = new Stage(app, 'MyStage', {
              env: {
                account: '123456789012',
                region: 'us-east-1'
              }
            });
            
            // both of these stacks will use the stage's account/region:
            // `.account` and `.region` will resolve to the concrete values as above
            new MyStack(myStage, 'Stack1');
            new YourStack(myStage, 'Stack2');
            
            // Define an environment-agnostic stack:
            // `.account` and `.region` will resolve to `{ "Ref": "AWS::AccountId" }` and `{ "Ref": "AWS::Region" }` respectively.
            // which will only resolve to actual values by CloudFormation during deployment.
            new MyStack(app, 'Stack1');
        '''
        result = self._values.get("env")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Environment], result)

    @builtins.property
    def permissions_boundary(
        self,
    ) -> typing.Optional[_aws_cdk_ceddda9d.PermissionsBoundary]:
        '''Options for applying a permissions boundary to all IAM Roles and Users created within this Stage.

        :default: - no permissions boundary is applied
        '''
        result = self._values.get("permissions_boundary")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.PermissionsBoundary], result)

    @builtins.property
    def stack_name(self) -> typing.Optional[builtins.str]:
        '''Name to deploy the stack with.

        :default: - Derived from construct path.
        '''
        result = self._values.get("stack_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def suppress_template_indentation(self) -> typing.Optional[builtins.bool]:
        '''Enable this flag to suppress indentation in generated CloudFormation templates.

        If not specified, the value of the ``@aws-cdk/core:suppressTemplateIndentation``
        context key will be used. If that is not specified, then the
        default value ``false`` will be used.

        :default: - the value of ``@aws-cdk/core:suppressTemplateIndentation``, or ``false`` if that is not set.
        '''
        result = self._values.get("suppress_template_indentation")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def synthesizer(self) -> typing.Optional[_aws_cdk_ceddda9d.IStackSynthesizer]:
        '''Synthesis method to use while deploying this stack.

        The Stack Synthesizer controls aspects of synthesis and deployment,
        like how assets are referenced and what IAM roles to use. For more
        information, see the README of the main CDK package.

        If not specified, the ``defaultStackSynthesizer`` from ``App`` will be used.
        If that is not specified, ``DefaultStackSynthesizer`` is used if
        ``@aws-cdk/core:newStyleStackSynthesis`` is set to ``true`` or the CDK major
        version is v2. In CDK v1 ``LegacyStackSynthesizer`` is the default if no
        other synthesizer is specified.

        :default: - The synthesizer specified on ``App``, or ``DefaultStackSynthesizer`` otherwise.
        '''
        result = self._values.get("synthesizer")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.IStackSynthesizer], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Stack tags that will be applied to all the taggable resources and the stack itself.

        :default: {}
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def termination_protection(self) -> typing.Optional[builtins.bool]:
        '''Whether to enable termination protection for this stack.

        :default: false
        '''
        result = self._values.get("termination_protection")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def monitoring(self) -> typing.Optional["MonitoringFacadeProps"]:
        '''(experimental) The monitoring configuration to apply to this stack.

        :default: - No monitoring.

        :stability: experimental
        '''
        result = self._values.get("monitoring")
        return typing.cast(typing.Optional["MonitoringFacadeProps"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "EntrypointStackProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(_aws_cdk_ceddda9d.IAspect)
class FargateServiceMonitoringAspect(
    metaclass=jsii.JSIIMeta,
    jsii_type="@condensetech/cdk-constructs.FargateServiceMonitoringAspect",
):
    '''(experimental) The FargateServiceMonitoringAspect iterates over the Fargate services and adds monitoring widgets and alarms.

    :stability: experimental
    '''

    def __init__(self, monitoring_facade: "ICondenseMonitoringFacade") -> None:
        '''
        :param monitoring_facade: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__630a342639fde7b8ddb7831e15c20bce6ca1d01d8e73643086815dda564a37af)
            check_type(argname="argument monitoring_facade", value=monitoring_facade, expected_type=type_hints["monitoring_facade"])
        jsii.create(self.__class__, self, [monitoring_facade])

    @jsii.member(jsii_name="overrideConfig")
    def override_config(
        self,
        node: _aws_cdk_aws_ecs_ceddda9d.FargateService,
        *,
        cpu_utilization_threshold: typing.Optional[jsii.Number] = None,
        memory_utilization: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''(experimental) Overrides the default configuration for a specific Fargate service.

        :param node: The Fargate service to monitor.
        :param cpu_utilization_threshold: (experimental) The CPU Utilization (%) threshold. Default: 90
        :param memory_utilization: (experimental) The Memory Utilization (%) threshold. Default: 90

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__08198ad4b3ada58ccbada9a586c23f0188d9bf3860baa47d1c58eb748e16020f)
            check_type(argname="argument node", value=node, expected_type=type_hints["node"])
        config = FargateServiceMonitoringConfig(
            cpu_utilization_threshold=cpu_utilization_threshold,
            memory_utilization=memory_utilization,
        )

        return typing.cast(None, jsii.invoke(self, "overrideConfig", [node, config]))

    @jsii.member(jsii_name="visit")
    def visit(self, node: _constructs_77d1e7e8.IConstruct) -> None:
        '''(experimental) All aspects can visit an IConstruct.

        :param node: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a5bf7c35fcf655cb700cb96318322e89f7fdcaae7658ed9df49af27c86903a83)
            check_type(argname="argument node", value=node, expected_type=type_hints["node"])
        return typing.cast(None, jsii.invoke(self, "visit", [node]))


@jsii.data_type(
    jsii_type="@condensetech/cdk-constructs.FargateServiceMonitoringConfig",
    jsii_struct_bases=[],
    name_mapping={
        "cpu_utilization_threshold": "cpuUtilizationThreshold",
        "memory_utilization": "memoryUtilization",
    },
)
class FargateServiceMonitoringConfig:
    def __init__(
        self,
        *,
        cpu_utilization_threshold: typing.Optional[jsii.Number] = None,
        memory_utilization: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''(experimental) The FargateServiceMonitoringConfig defines the thresholds for the Fargate service monitoring.

        :param cpu_utilization_threshold: (experimental) The CPU Utilization (%) threshold. Default: 90
        :param memory_utilization: (experimental) The Memory Utilization (%) threshold. Default: 90

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5d9c95dc69a12f04e36f92d0cb68fcee773eb13b67f2286aae9b9484c660ca8b)
            check_type(argname="argument cpu_utilization_threshold", value=cpu_utilization_threshold, expected_type=type_hints["cpu_utilization_threshold"])
            check_type(argname="argument memory_utilization", value=memory_utilization, expected_type=type_hints["memory_utilization"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if cpu_utilization_threshold is not None:
            self._values["cpu_utilization_threshold"] = cpu_utilization_threshold
        if memory_utilization is not None:
            self._values["memory_utilization"] = memory_utilization

    @builtins.property
    def cpu_utilization_threshold(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The CPU Utilization (%) threshold.

        :default: 90

        :stability: experimental
        '''
        result = self._values.get("cpu_utilization_threshold")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def memory_utilization(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The Memory Utilization (%) threshold.

        :default: 90

        :stability: experimental
        '''
        result = self._values.get("memory_utilization")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "FargateServiceMonitoringConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.interface(
    jsii_type="@condensetech/cdk-constructs.IApplicationListenerPriorityAllocator"
)
class IApplicationListenerPriorityAllocator(typing_extensions.Protocol):
    '''
    :stability: experimental
    '''

    @builtins.property
    @jsii.member(jsii_name="serviceToken")
    def service_token(self) -> builtins.str:
        '''(experimental) The service token to use to reference the custom resource.

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="allocatePriority")
    def allocate_priority(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        priority: typing.Optional[jsii.Number] = None,
    ) -> jsii.Number:
        '''(experimental) Allocates the priority of an application listener rule.

        :param scope: The scope of the construct.
        :param id: The ID of the listener rule to allocate the priority to.
        :param priority: (experimental) The priority to allocate. Default: a priority will be allocated automatically.

        :return: The allocated priority.

        :stability: experimental
        '''
        ...


class _IApplicationListenerPriorityAllocatorProxy:
    '''
    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@condensetech/cdk-constructs.IApplicationListenerPriorityAllocator"

    @builtins.property
    @jsii.member(jsii_name="serviceToken")
    def service_token(self) -> builtins.str:
        '''(experimental) The service token to use to reference the custom resource.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "serviceToken"))

    @jsii.member(jsii_name="allocatePriority")
    def allocate_priority(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        priority: typing.Optional[jsii.Number] = None,
    ) -> jsii.Number:
        '''(experimental) Allocates the priority of an application listener rule.

        :param scope: The scope of the construct.
        :param id: The ID of the listener rule to allocate the priority to.
        :param priority: (experimental) The priority to allocate. Default: a priority will be allocated automatically.

        :return: The allocated priority.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__81990a8032fc66ef4e810f42acc7e5d213a2914b89e2cdee1ba98e0eea19d6bb)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = AllocatePriorityProps(priority=priority)

        return typing.cast(jsii.Number, jsii.invoke(self, "allocatePriority", [scope, id, props]))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IApplicationListenerPriorityAllocator).__jsii_proxy_class__ = lambda : _IApplicationListenerPriorityAllocatorProxy


@jsii.interface(jsii_type="@condensetech/cdk-constructs.ICondenseMonitoringFacade")
class ICondenseMonitoringFacade(typing_extensions.Protocol):
    '''(experimental) The ICondenseMonitoringFacade interface defines the methods that the monitoring facade must implement.

    :stability: experimental
    '''

    @builtins.property
    @jsii.member(jsii_name="dashboard")
    def dashboard(self) -> _aws_cdk_aws_cloudwatch_ceddda9d.Dashboard:
        '''(experimental) Returns the Cloudwatch dashboard to be used for this stack monitoring.

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="addAlarm")
    def add_alarm(self, alarm: _aws_cdk_aws_cloudwatch_ceddda9d.Alarm) -> None:
        '''(experimental) Add an alarm to the monitoring facade, by linking it to the alarms topic.

        :param alarm: The alarm to add.

        :stability: experimental
        '''
        ...


class _ICondenseMonitoringFacadeProxy:
    '''(experimental) The ICondenseMonitoringFacade interface defines the methods that the monitoring facade must implement.

    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@condensetech/cdk-constructs.ICondenseMonitoringFacade"

    @builtins.property
    @jsii.member(jsii_name="dashboard")
    def dashboard(self) -> _aws_cdk_aws_cloudwatch_ceddda9d.Dashboard:
        '''(experimental) Returns the Cloudwatch dashboard to be used for this stack monitoring.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Dashboard, jsii.get(self, "dashboard"))

    @jsii.member(jsii_name="addAlarm")
    def add_alarm(self, alarm: _aws_cdk_aws_cloudwatch_ceddda9d.Alarm) -> None:
        '''(experimental) Add an alarm to the monitoring facade, by linking it to the alarms topic.

        :param alarm: The alarm to add.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ae0302a7c36b248336045bd8c22ffdffd2a485c1a8b47c60c0ce68946566b028)
            check_type(argname="argument alarm", value=alarm, expected_type=type_hints["alarm"])
        return typing.cast(None, jsii.invoke(self, "addAlarm", [alarm]))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, ICondenseMonitoringFacade).__jsii_proxy_class__ = lambda : _ICondenseMonitoringFacadeProxy


@jsii.interface(jsii_type="@condensetech/cdk-constructs.IDatabase")
class IDatabase(_aws_cdk_aws_ec2_ceddda9d.IConnectable, typing_extensions.Protocol):
    '''(experimental) The IDatabase interface allows to write stacks and constructs that depend on a database without being tied to the specific database implementation.

    :stability: experimental

    Example::

        // In this example, MyConstruct is used across several IDatabase implementations without being tied to a specific construct or stack
        
        interface MyProps {
          database: IDatabase;
        }
        
        class MyConstruct extends Construct {
          constructor(scope: Construct, id: string, props: MyProps) {
           super(scope, id);
           new CfnOutput(this, 'DatabaseEndpoint', { value: props.database.endpoint.hostname });
          }
        }
        
        interface MyStackProps {
          database3: IDatabase;
        }
        
        class MyStack extends cdk.Stack {
          constructor(scope: Construct, id: string, props: MyStackProps) {
            super(scope, id, props);
            new MyConstruct(this, 'MyConstruct1', {
              database: new AuroraCluster(this, 'Database', { ... })
            });
            new MyConstruct(this, 'MyConstruct2', {
              database: new DatabaseInstance(this, 'Database', { ... })
            });
            new MyConstruct(this, 'MyConstruct3', {
               database: props.database3
            });
          }
        }
        
        const database3 = new AuroraClustrStack(app, 'AuroraClusterStack', { ... });
        new MyStack(app, 'MyStack', { database3 });
    '''

    @builtins.property
    @jsii.member(jsii_name="endpoint")
    def endpoint(self) -> _aws_cdk_aws_rds_ceddda9d.Endpoint:
        '''(experimental) The endpoint of the database.

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="fetchSecret")
    def fetch_secret(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: typing.Optional[builtins.str] = None,
    ) -> _aws_cdk_aws_secretsmanager_ceddda9d.ISecret:
        '''(experimental) Utility method that returns the secret with the credentials to access the database in a cross-stack compatible way.

        :param scope: -
        :param id: -

        :stability: experimental
        '''
        ...


class _IDatabaseProxy(
    jsii.proxy_for(_aws_cdk_aws_ec2_ceddda9d.IConnectable), # type: ignore[misc]
):
    '''(experimental) The IDatabase interface allows to write stacks and constructs that depend on a database without being tied to the specific database implementation.

    :stability: experimental

    Example::

        // In this example, MyConstruct is used across several IDatabase implementations without being tied to a specific construct or stack
        
        interface MyProps {
          database: IDatabase;
        }
        
        class MyConstruct extends Construct {
          constructor(scope: Construct, id: string, props: MyProps) {
           super(scope, id);
           new CfnOutput(this, 'DatabaseEndpoint', { value: props.database.endpoint.hostname });
          }
        }
        
        interface MyStackProps {
          database3: IDatabase;
        }
        
        class MyStack extends cdk.Stack {
          constructor(scope: Construct, id: string, props: MyStackProps) {
            super(scope, id, props);
            new MyConstruct(this, 'MyConstruct1', {
              database: new AuroraCluster(this, 'Database', { ... })
            });
            new MyConstruct(this, 'MyConstruct2', {
              database: new DatabaseInstance(this, 'Database', { ... })
            });
            new MyConstruct(this, 'MyConstruct3', {
               database: props.database3
            });
          }
        }
        
        const database3 = new AuroraClustrStack(app, 'AuroraClusterStack', { ... });
        new MyStack(app, 'MyStack', { database3 });
    '''

    __jsii_type__: typing.ClassVar[str] = "@condensetech/cdk-constructs.IDatabase"

    @builtins.property
    @jsii.member(jsii_name="endpoint")
    def endpoint(self) -> _aws_cdk_aws_rds_ceddda9d.Endpoint:
        '''(experimental) The endpoint of the database.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_rds_ceddda9d.Endpoint, jsii.get(self, "endpoint"))

    @jsii.member(jsii_name="fetchSecret")
    def fetch_secret(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: typing.Optional[builtins.str] = None,
    ) -> _aws_cdk_aws_secretsmanager_ceddda9d.ISecret:
        '''(experimental) Utility method that returns the secret with the credentials to access the database in a cross-stack compatible way.

        :param scope: -
        :param id: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2987d0fa60464de1815bbddfeb2c93d14ecf75f24cf21f876ac433bfda2c54a6)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        return typing.cast(_aws_cdk_aws_secretsmanager_ceddda9d.ISecret, jsii.invoke(self, "fetchSecret", [scope, id]))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IDatabase).__jsii_proxy_class__ = lambda : _IDatabaseProxy


@jsii.interface(jsii_type="@condensetech/cdk-constructs.IEntrypoint")
class IEntrypoint(typing_extensions.Protocol):
    '''(experimental) The Entrypoint LoadBalancer is an Application Load Balancer (ALB) that serves as the centralized entry point for all applications.

    This ALB is shared across multiple applications, primarily to optimize infrastructure costs by reducing the need for multiple load balancers.

    The IEntrypoint interface defines the common behaviors and properties that various implementations must adhere to.
    This allows stacks and constructs to interact with the entry point without being dependent on a specific implementation, ensuring greater flexibility and maintainability.

    :stability: experimental
    '''

    @builtins.property
    @jsii.member(jsii_name="alb")
    def alb(
        self,
    ) -> _aws_cdk_aws_elasticloadbalancingv2_ceddda9d.IApplicationLoadBalancer:
        '''(experimental) The ALB that serves as the entrypoint.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="domainName")
    def domain_name(self) -> builtins.str:
        '''(experimental) The load balancer custom domain name.

        :default: - No domain name is specified, and the load balancer dns name is used.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="priorityAllocator")
    def priority_allocator(self) -> IApplicationListenerPriorityAllocator:
        '''(experimental) The Application Listener priority allocator for the entrypoint.

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="allocateListenerRule")
    def allocate_listener_rule(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        action: typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ListenerAction] = None,
        conditions: typing.Optional[typing.Sequence[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ListenerCondition]] = None,
        priority: typing.Optional[jsii.Number] = None,
        target_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.IApplicationTargetGroup]] = None,
    ) -> _aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ApplicationListenerRule:
        '''(experimental) It creates an ApplicationListenerRule for the HTTPS listener of the Entrypoint.

        This method doesn't require a priority to be explicitly set, and tracks the allocated priorities on a DynamoDB table to avoid conflicts.

        :param scope: The scope of the construct.
        :param id: The application listener rule.
        :param action: (experimental) Action to perform when requests are received. Only one of ``action``, ``fixedResponse``, ``redirectResponse`` or ``targetGroups`` can be specified. Default: - No action
        :param conditions: (experimental) Rule applies if matches the conditions. Default: - No conditions.
        :param priority: (experimental) Priority of the rule. The rule with the lowest priority will be used for every request. Default: - The rule will be assigned a priority automatically.
        :param target_groups: (experimental) Target groups to forward requests to. Only one of ``action``, ``fixedResponse``, ``redirectResponse`` or ``targetGroups`` can be specified. Implies a ``forward`` action. Default: - No target groups.

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="referenceListener")
    def reference_listener(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
    ) -> _aws_cdk_aws_elasticloadbalancingv2_ceddda9d.IApplicationListener:
        '''(experimental) Utility method that returns the HTTPS listener of the entrypoint in a cross-stack compatible way.

        :param scope: -
        :param id: -

        :stability: experimental
        '''
        ...


class _IEntrypointProxy:
    '''(experimental) The Entrypoint LoadBalancer is an Application Load Balancer (ALB) that serves as the centralized entry point for all applications.

    This ALB is shared across multiple applications, primarily to optimize infrastructure costs by reducing the need for multiple load balancers.

    The IEntrypoint interface defines the common behaviors and properties that various implementations must adhere to.
    This allows stacks and constructs to interact with the entry point without being dependent on a specific implementation, ensuring greater flexibility and maintainability.

    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@condensetech/cdk-constructs.IEntrypoint"

    @builtins.property
    @jsii.member(jsii_name="alb")
    def alb(
        self,
    ) -> _aws_cdk_aws_elasticloadbalancingv2_ceddda9d.IApplicationLoadBalancer:
        '''(experimental) The ALB that serves as the entrypoint.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.IApplicationLoadBalancer, jsii.get(self, "alb"))

    @builtins.property
    @jsii.member(jsii_name="domainName")
    def domain_name(self) -> builtins.str:
        '''(experimental) The load balancer custom domain name.

        :default: - No domain name is specified, and the load balancer dns name is used.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "domainName"))

    @builtins.property
    @jsii.member(jsii_name="priorityAllocator")
    def priority_allocator(self) -> IApplicationListenerPriorityAllocator:
        '''(experimental) The Application Listener priority allocator for the entrypoint.

        :stability: experimental
        '''
        return typing.cast(IApplicationListenerPriorityAllocator, jsii.get(self, "priorityAllocator"))

    @jsii.member(jsii_name="allocateListenerRule")
    def allocate_listener_rule(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        action: typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ListenerAction] = None,
        conditions: typing.Optional[typing.Sequence[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ListenerCondition]] = None,
        priority: typing.Optional[jsii.Number] = None,
        target_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.IApplicationTargetGroup]] = None,
    ) -> _aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ApplicationListenerRule:
        '''(experimental) It creates an ApplicationListenerRule for the HTTPS listener of the Entrypoint.

        This method doesn't require a priority to be explicitly set, and tracks the allocated priorities on a DynamoDB table to avoid conflicts.

        :param scope: The scope of the construct.
        :param id: The application listener rule.
        :param action: (experimental) Action to perform when requests are received. Only one of ``action``, ``fixedResponse``, ``redirectResponse`` or ``targetGroups`` can be specified. Default: - No action
        :param conditions: (experimental) Rule applies if matches the conditions. Default: - No conditions.
        :param priority: (experimental) Priority of the rule. The rule with the lowest priority will be used for every request. Default: - The rule will be assigned a priority automatically.
        :param target_groups: (experimental) Target groups to forward requests to. Only one of ``action``, ``fixedResponse``, ``redirectResponse`` or ``targetGroups`` can be specified. Implies a ``forward`` action. Default: - No target groups.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4008bd74f518e6bfa2d805893a8dde6ba0d0f034c8d31f73351f2c31441f556b)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = AllocateApplicationListenerRuleProps(
            action=action,
            conditions=conditions,
            priority=priority,
            target_groups=target_groups,
        )

        return typing.cast(_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ApplicationListenerRule, jsii.invoke(self, "allocateListenerRule", [scope, id, props]))

    @jsii.member(jsii_name="referenceListener")
    def reference_listener(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
    ) -> _aws_cdk_aws_elasticloadbalancingv2_ceddda9d.IApplicationListener:
        '''(experimental) Utility method that returns the HTTPS listener of the entrypoint in a cross-stack compatible way.

        :param scope: -
        :param id: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__02f32d7fdaba44b683a7d540d6ef577e3716c742002e81f804746bc7973e65fa)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        return typing.cast(_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.IApplicationListener, jsii.invoke(self, "referenceListener", [scope, id]))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IEntrypoint).__jsii_proxy_class__ = lambda : _IEntrypointProxy


@jsii.interface(jsii_type="@condensetech/cdk-constructs.INetworking")
class INetworking(typing_extensions.Protocol):
    '''(experimental) The INetworking interface allows to write stacks and constructs that depend on networking without being tied to the specific networking implementation.

    This allows to write composable infrastructures that, depending on the scenario, can split the networking layer in a separate stack or in a construct.

    In addition, the INetworking interface imposes a set of properties to ease the development of constructs that depend on networking resources.

    :stability: experimental
    '''

    @builtins.property
    @jsii.member(jsii_name="hasPrivateSubnets")
    def has_private_subnets(self) -> builtins.bool:
        '''(experimental) Returns if the VPC has private subnets (with access to internet through a NAT gateway).

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="isolatedSubnets")
    def isolated_subnets(self) -> _aws_cdk_aws_ec2_ceddda9d.SubnetSelection:
        '''(experimental) Returns the isolated subnets of the VPC (without access to internet).

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="publicSubnets")
    def public_subnets(self) -> _aws_cdk_aws_ec2_ceddda9d.SubnetSelection:
        '''(experimental) Returns the public subnets of the VPC.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="vpc")
    def vpc(self) -> _aws_cdk_aws_ec2_ceddda9d.IVpc:
        '''(experimental) The VPC where the networking resources are created.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="bastionHost")
    def bastion_host(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IConnectable]:
        '''(experimental) Returns the bastion host instance of the VPC, if any.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="privateSubnets")
    def private_subnets(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection]:
        '''(experimental) Returns the private subnets of the VPC (with access to internet through a NAT gateway).

        :stability: experimental
        '''
        ...


class _INetworkingProxy:
    '''(experimental) The INetworking interface allows to write stacks and constructs that depend on networking without being tied to the specific networking implementation.

    This allows to write composable infrastructures that, depending on the scenario, can split the networking layer in a separate stack or in a construct.

    In addition, the INetworking interface imposes a set of properties to ease the development of constructs that depend on networking resources.

    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@condensetech/cdk-constructs.INetworking"

    @builtins.property
    @jsii.member(jsii_name="hasPrivateSubnets")
    def has_private_subnets(self) -> builtins.bool:
        '''(experimental) Returns if the VPC has private subnets (with access to internet through a NAT gateway).

        :stability: experimental
        '''
        return typing.cast(builtins.bool, jsii.get(self, "hasPrivateSubnets"))

    @builtins.property
    @jsii.member(jsii_name="isolatedSubnets")
    def isolated_subnets(self) -> _aws_cdk_aws_ec2_ceddda9d.SubnetSelection:
        '''(experimental) Returns the isolated subnets of the VPC (without access to internet).

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, jsii.get(self, "isolatedSubnets"))

    @builtins.property
    @jsii.member(jsii_name="publicSubnets")
    def public_subnets(self) -> _aws_cdk_aws_ec2_ceddda9d.SubnetSelection:
        '''(experimental) Returns the public subnets of the VPC.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, jsii.get(self, "publicSubnets"))

    @builtins.property
    @jsii.member(jsii_name="vpc")
    def vpc(self) -> _aws_cdk_aws_ec2_ceddda9d.IVpc:
        '''(experimental) The VPC where the networking resources are created.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.IVpc, jsii.get(self, "vpc"))

    @builtins.property
    @jsii.member(jsii_name="bastionHost")
    def bastion_host(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IConnectable]:
        '''(experimental) Returns the bastion host instance of the VPC, if any.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IConnectable], jsii.get(self, "bastionHost"))

    @builtins.property
    @jsii.member(jsii_name="privateSubnets")
    def private_subnets(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection]:
        '''(experimental) Returns the private subnets of the VPC (with access to internet through a NAT gateway).

        :stability: experimental
        '''
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection], jsii.get(self, "privateSubnets"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, INetworking).__jsii_proxy_class__ = lambda : _INetworkingProxy


@jsii.implements(ICondenseMonitoringFacade)
class MonitoringFacade(
    metaclass=jsii.JSIIMeta,
    jsii_type="@condensetech/cdk-constructs.MonitoringFacade",
):
    '''(experimental) The MonitoringFacade creates a Cloudwatch dashboard and applies monitoring aspects to resources.

    These aspects will scan for resources, create alarms and add metrics to the MonitoringFacade dashboard.

    This allow to have a centralized monitoring configuration for all resources in the stack.

    Additionally, the ``config*`` methods allow to override the default configuration for a specific resource.

    :stability: experimental

    Example::

        class MyStack extends cdk.Stack {
          constructor(scope: Construct, id: string, props: cdk.StackProps) {
            super(scope, id, props);
        
            const cluster = new AuroraCluster(this, 'DatabaseCluster', { ... });
        
            // Even if the MonitoringFacade is built after the AuroraCluster, the cluster will be monitored, because the aspects are executed after the stack is built.
            const monitoring = new MonitoringFacade(this, { topicArn: 'arn:aws:sns:us-east-1:123456789012:MyTopic' });
        
            const cluster2 = new AuroraCluster(this, 'DatabaseCluster2', { ... });
            // The monitoring configuration for the second cluster is modified so that the CPU utilization alarm is triggered when the utilization is over the 10%.
            monitoring.configRdsCluster(cluster2, {
              cpuUtilizationThreshold: 0.1,
            });
          }
        }
    '''

    def __init__(
        self,
        scope: _aws_cdk_ceddda9d.Stack,
        *,
        topic_arn: builtins.str,
        dashboard_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param topic_arn: (experimental) The ARN of the SNS topic to use for alarms.
        :param dashboard_name: (experimental) The name of the Cloudwatch dashboard to create. Default: - A name is generated by CDK.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5b60432f85a285be42a21b1122e88974bc2b20a98b76d5e0ee45cf7af2cd144e)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
        props = MonitoringFacadeProps(
            topic_arn=topic_arn, dashboard_name=dashboard_name
        )

        jsii.create(self.__class__, self, [scope, props])

    @jsii.member(jsii_name="of")
    @builtins.classmethod
    def of(
        cls,
        scope: _constructs_77d1e7e8.Construct,
    ) -> typing.Optional["MonitoringFacade"]:
        '''
        :param scope: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__062fb685fcb23a28ff48a011c2571420172c27726b513c0a6b3319958ed71380)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
        return typing.cast(typing.Optional["MonitoringFacade"], jsii.sinvoke(cls, "of", [scope]))

    @jsii.member(jsii_name="addAlarm")
    def add_alarm(self, alarm: _aws_cdk_aws_cloudwatch_ceddda9d.Alarm) -> None:
        '''(experimental) Add an alarm to the monitoring facade, by linking it to the alarms topic.

        :param alarm: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dcb66ac5e0587112880aa0994495745143d5d9118d1dda39610f56b7520fea2d)
            check_type(argname="argument alarm", value=alarm, expected_type=type_hints["alarm"])
        return typing.cast(None, jsii.invoke(self, "addAlarm", [alarm]))

    @jsii.member(jsii_name="configApplicationLoadBalancer")
    def config_application_load_balancer(
        self,
        resource: _aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ApplicationLoadBalancer,
        *,
        redirect_url_limit_exceeded_threshold: typing.Optional[jsii.Number] = None,
        rejected_connections_threshold: typing.Optional[jsii.Number] = None,
        response_time_threshold: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        target5xx_errors_threshold: typing.Optional[jsii.Number] = None,
        target_connection_errors_threshold: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''(experimental) Overrides the default configuration for a specific Application Load Balancer.

        :param resource: The ALB to monitor.
        :param redirect_url_limit_exceeded_threshold: (experimental) The Redirect URL Limit Exceeded threshold. Default: 0
        :param rejected_connections_threshold: (experimental) The Rejected Connections threshold. Default: 0
        :param response_time_threshold: (experimental) The Response Time threshold. Default: - No threshold.
        :param target5xx_errors_threshold: (experimental) The 5xx Errors threshold. Default: 0
        :param target_connection_errors_threshold: (experimental) The Target Connection Errors threshold. Default: 0

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__da7e650bffb023ec1deaa3822cc1807824bfbea19fe8bd4d8e9c1befa0714e5d)
            check_type(argname="argument resource", value=resource, expected_type=type_hints["resource"])
        config = ApplicationLoadBalancerMonitoringConfig(
            redirect_url_limit_exceeded_threshold=redirect_url_limit_exceeded_threshold,
            rejected_connections_threshold=rejected_connections_threshold,
            response_time_threshold=response_time_threshold,
            target5xx_errors_threshold=target5xx_errors_threshold,
            target_connection_errors_threshold=target_connection_errors_threshold,
        )

        return typing.cast(None, jsii.invoke(self, "configApplicationLoadBalancer", [resource, config]))

    @jsii.member(jsii_name="configCacheCluster")
    def config_cache_cluster(
        self,
        resource: _aws_cdk_aws_elasticache_ceddda9d.CfnCacheCluster,
        *,
        cpu_utilization_threshold: typing.Optional[jsii.Number] = None,
        engine_cpu_utilization_threshold: typing.Optional[jsii.Number] = None,
        max_connections_threshold: typing.Optional[jsii.Number] = None,
        memory_usage_threshold: typing.Optional[jsii.Number] = None,
        replication_lag_threshold: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    ) -> None:
        '''(experimental) Overrides the default configuration for a specific Elasticache cluster.

        :param resource: The elasticache cluster to monitor.
        :param cpu_utilization_threshold: (experimental) The CPU Utilization (%) threshold. Default: 90
        :param engine_cpu_utilization_threshold: (experimental) The Engine CPU Utilization (%) threshold. Default: 95
        :param max_connections_threshold: (experimental) The Max Connections threshold. Default: 60,000
        :param memory_usage_threshold: (experimental) The Memory Usage (%) threshold. Default: 90
        :param replication_lag_threshold: (experimental) The Replication Lag threshold. Default: - No threshold.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__77ae16eef5ef965347724604827c8f4ef09950c27eb1383a996fc45847172b85)
            check_type(argname="argument resource", value=resource, expected_type=type_hints["resource"])
        config = CacheClusterMonitoringConfig(
            cpu_utilization_threshold=cpu_utilization_threshold,
            engine_cpu_utilization_threshold=engine_cpu_utilization_threshold,
            max_connections_threshold=max_connections_threshold,
            memory_usage_threshold=memory_usage_threshold,
            replication_lag_threshold=replication_lag_threshold,
        )

        return typing.cast(None, jsii.invoke(self, "configCacheCluster", [resource, config]))

    @jsii.member(jsii_name="configFargateService")
    def config_fargate_service(
        self,
        resource: _aws_cdk_aws_ecs_ceddda9d.FargateService,
        *,
        cpu_utilization_threshold: typing.Optional[jsii.Number] = None,
        memory_utilization: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''(experimental) Overrides the default configuration for a specific ECS Fargate service.

        :param resource: The Fargate service to monitor.
        :param cpu_utilization_threshold: (experimental) The CPU Utilization (%) threshold. Default: 90
        :param memory_utilization: (experimental) The Memory Utilization (%) threshold. Default: 90

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cc5797e8af3aea6b37a46a23ca01873dd31f7c7f1fd5d8d4c5329140146598af)
            check_type(argname="argument resource", value=resource, expected_type=type_hints["resource"])
        config = FargateServiceMonitoringConfig(
            cpu_utilization_threshold=cpu_utilization_threshold,
            memory_utilization=memory_utilization,
        )

        return typing.cast(None, jsii.invoke(self, "configFargateService", [resource, config]))

    @jsii.member(jsii_name="configRdsCluster")
    def config_rds_cluster(
        self,
        resource: _aws_cdk_aws_rds_ceddda9d.DatabaseCluster,
        *,
        cpu_utilization_threshold: typing.Optional[jsii.Number] = None,
        ebs_byte_balance_threshold: typing.Optional[jsii.Number] = None,
        ebs_io_balance_threshold: typing.Optional[jsii.Number] = None,
        freeable_memory_threshold: typing.Optional[_aws_cdk_ceddda9d.Size] = None,
        max_connections_threshold: typing.Optional[jsii.Number] = None,
        read_latency_threshold: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''(experimental) Overrides the default configuration for a specific RDS cluster.

        :param resource: The RDS cluster to monitor.
        :param cpu_utilization_threshold: (experimental) The CPU Utilization (%) threshold. Default: 90
        :param ebs_byte_balance_threshold: (experimental) The EBS Byte Balance (%) threshold. Default: 10
        :param ebs_io_balance_threshold: (experimental) The EBS IO Balance (%) threshold. Default: 10
        :param freeable_memory_threshold: (experimental) The Freeable Memory threshold. Default: 100 MiB
        :param max_connections_threshold: (experimental) The Max Connections threshold. Default: 50
        :param read_latency_threshold: (experimental) The Read Latency threshold. Default: 20

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__04d4a4a7106da61f61e3c6b31bd24cfe6700fe524ec7109cd343ec0d17386af1)
            check_type(argname="argument resource", value=resource, expected_type=type_hints["resource"])
        config = RdsClusterMonitoringConfig(
            cpu_utilization_threshold=cpu_utilization_threshold,
            ebs_byte_balance_threshold=ebs_byte_balance_threshold,
            ebs_io_balance_threshold=ebs_io_balance_threshold,
            freeable_memory_threshold=freeable_memory_threshold,
            max_connections_threshold=max_connections_threshold,
            read_latency_threshold=read_latency_threshold,
        )

        return typing.cast(None, jsii.invoke(self, "configRdsCluster", [resource, config]))

    @jsii.member(jsii_name="configRdsInstance")
    def config_rds_instance(
        self,
        resource: _aws_cdk_aws_rds_ceddda9d.DatabaseInstance,
        *,
        cpu_utilization_threshold: typing.Optional[jsii.Number] = None,
        ebs_byte_balance_threshold: typing.Optional[jsii.Number] = None,
        ebs_io_balance_threshold: typing.Optional[jsii.Number] = None,
        freeable_memory_threshold: typing.Optional[_aws_cdk_ceddda9d.Size] = None,
        free_storage_space_threshold: typing.Optional[_aws_cdk_ceddda9d.Size] = None,
        max_connections_threshold: typing.Optional[jsii.Number] = None,
        read_latency_threshold: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''(experimental) Overrides the default configuration for a specific RDS instance.

        :param resource: The RDS instance to monitor.
        :param cpu_utilization_threshold: (experimental) The CPU Utilization (%) threshold. Default: 90
        :param ebs_byte_balance_threshold: (experimental) The EBS Byte Balance (%) threshold. Default: 10
        :param ebs_io_balance_threshold: (experimental) The EBS IO Balance (%) threshold. Default: 10
        :param freeable_memory_threshold: (experimental) The Freeable Memory threshold. Default: 100 MiB
        :param free_storage_space_threshold: (experimental) The Free Storage Space threshold. Default: 100 MiB
        :param max_connections_threshold: (experimental) The Max Connections threshold. Default: 50
        :param read_latency_threshold: (experimental) The Read Latency threshold. Default: 20

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e6ca11cc84243de70b6f802cf22bd5a857a72dd9ee192b19d200ea6908f75205)
            check_type(argname="argument resource", value=resource, expected_type=type_hints["resource"])
        config = RdsInstanceMonitoringConfig(
            cpu_utilization_threshold=cpu_utilization_threshold,
            ebs_byte_balance_threshold=ebs_byte_balance_threshold,
            ebs_io_balance_threshold=ebs_io_balance_threshold,
            freeable_memory_threshold=freeable_memory_threshold,
            free_storage_space_threshold=free_storage_space_threshold,
            max_connections_threshold=max_connections_threshold,
            read_latency_threshold=read_latency_threshold,
        )

        return typing.cast(None, jsii.invoke(self, "configRdsInstance", [resource, config]))

    @jsii.member(jsii_name="configTargetGroup")
    def config_target_group(
        self,
        resource: _aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ApplicationTargetGroup,
        *,
        min_healthy_hosts_threshold: typing.Optional[jsii.Number] = None,
        response_time_threshold: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    ) -> None:
        '''(experimental) Overrides the default configuration for a specific ELBv2 Target Group.

        :param resource: The target group to monitor.
        :param min_healthy_hosts_threshold: (experimental) The Min Healthy Hosts threshold. Default: 1
        :param response_time_threshold: (experimental) The Response Time threshold. Default: - No threshold.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cbda6ebd99f677bf0faefa48f330959fb4c1e31fbc4ef282ced8cb8a8312f7d8)
            check_type(argname="argument resource", value=resource, expected_type=type_hints["resource"])
        config = TargetGroupMonitoringConfig(
            min_healthy_hosts_threshold=min_healthy_hosts_threshold,
            response_time_threshold=response_time_threshold,
        )

        return typing.cast(None, jsii.invoke(self, "configTargetGroup", [resource, config]))

    @builtins.property
    @jsii.member(jsii_name="alarmTopic")
    def alarm_topic(self) -> _aws_cdk_aws_sns_ceddda9d.ITopic:
        '''
        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_sns_ceddda9d.ITopic, jsii.get(self, "alarmTopic"))

    @builtins.property
    @jsii.member(jsii_name="dashboard")
    def dashboard(self) -> _aws_cdk_aws_cloudwatch_ceddda9d.Dashboard:
        '''(experimental) Returns the Cloudwatch dashboard to be used for this stack monitoring.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Dashboard, jsii.get(self, "dashboard"))


@jsii.data_type(
    jsii_type="@condensetech/cdk-constructs.MonitoringFacadeProps",
    jsii_struct_bases=[],
    name_mapping={"topic_arn": "topicArn", "dashboard_name": "dashboardName"},
)
class MonitoringFacadeProps:
    def __init__(
        self,
        *,
        topic_arn: builtins.str,
        dashboard_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Properties for the MonitoringFacade.

        :param topic_arn: (experimental) The ARN of the SNS topic to use for alarms.
        :param dashboard_name: (experimental) The name of the Cloudwatch dashboard to create. Default: - A name is generated by CDK.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__24412f7336ded0c019fb4a3d9571528862b33059004b84acdee1f6ddefaf66e1)
            check_type(argname="argument topic_arn", value=topic_arn, expected_type=type_hints["topic_arn"])
            check_type(argname="argument dashboard_name", value=dashboard_name, expected_type=type_hints["dashboard_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "topic_arn": topic_arn,
        }
        if dashboard_name is not None:
            self._values["dashboard_name"] = dashboard_name

    @builtins.property
    def topic_arn(self) -> builtins.str:
        '''(experimental) The ARN of the SNS topic to use for alarms.

        :stability: experimental
        '''
        result = self._values.get("topic_arn")
        assert result is not None, "Required property 'topic_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def dashboard_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of the Cloudwatch dashboard to create.

        :default: - A name is generated by CDK.

        :stability: experimental
        '''
        result = self._values.get("dashboard_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MonitoringFacadeProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class NaiveBasicAuthCloudfrontFunction(
    _aws_cdk_aws_cloudfront_ceddda9d.Function,
    metaclass=jsii.JSIIMeta,
    jsii_type="@condensetech/cdk-constructs.NaiveBasicAuthCloudfrontFunction",
):
    '''(experimental) A CloudFront function that implements a naive basic auth mechanism.

    The function is naive because the basic auth string isn't treated as a secret and it's hardcoded in the function code.

    This function is useful for simple use cases where you need to protect a CloudFront distribution with basic auth. A typical use case is to ensure that a staging environment isn't indexed by crawlers (just in case robots.txt is totally ignored).

    :stability: experimental
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        basic_auth_string: builtins.str,
        exclude_paths: typing.Optional[typing.Sequence[typing.Union["NaiveBasicAuthCloudfrontFunctionExcludedPath", typing.Dict[builtins.str, typing.Any]]]] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param basic_auth_string: (experimental) The basic auth string to use for checking basic auth credentials You can generate a basic auth string using the following command: echo -n "$username:$password" | base64.
        :param exclude_paths: (experimental) The paths to exclude from basic auth. Pass a string or regex to match the path. Strings are checked using === operator. Default: - no paths are excluded

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2a83db3b7239cac1a1fa2230e335342bae58153ab2fb6a02426375af19d34898)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = NaiveBasicAuthCloudfrontFunctionProps(
            basic_auth_string=basic_auth_string, exclude_paths=exclude_paths
        )

        jsii.create(self.__class__, self, [scope, id, props])


@jsii.data_type(
    jsii_type="@condensetech/cdk-constructs.NaiveBasicAuthCloudfrontFunctionExcludedPath",
    jsii_struct_bases=[],
    name_mapping={"path": "path", "match_mode": "matchMode"},
)
class NaiveBasicAuthCloudfrontFunctionExcludedPath:
    def __init__(
        self,
        *,
        path: builtins.str,
        match_mode: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Exclusion path for the NaiveBasicAuthCloudfrontFunction.

        :param path: (experimental) The path to exclude from basic auth.
        :param match_mode: (experimental) The match mode to use for the path: - 'exact' for exact string match - 'regex' for regex match. Default: 'exact'

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2d7ee86e24b43210088ff0e7d04520ac486945cb13c7906b88b1b91a7e740d50)
            check_type(argname="argument path", value=path, expected_type=type_hints["path"])
            check_type(argname="argument match_mode", value=match_mode, expected_type=type_hints["match_mode"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "path": path,
        }
        if match_mode is not None:
            self._values["match_mode"] = match_mode

    @builtins.property
    def path(self) -> builtins.str:
        '''(experimental) The path to exclude from basic auth.

        :stability: experimental

        Example::

            "/admin"
            "/\/admin\\/.+/"
        '''
        result = self._values.get("path")
        assert result is not None, "Required property 'path' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def match_mode(self) -> typing.Optional[builtins.str]:
        '''(experimental) The match mode to use for the path: - 'exact' for exact string match - 'regex' for regex match.

        :default: 'exact'

        :stability: experimental
        '''
        result = self._values.get("match_mode")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NaiveBasicAuthCloudfrontFunctionExcludedPath(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@condensetech/cdk-constructs.NaiveBasicAuthCloudfrontFunctionProps",
    jsii_struct_bases=[],
    name_mapping={
        "basic_auth_string": "basicAuthString",
        "exclude_paths": "excludePaths",
    },
)
class NaiveBasicAuthCloudfrontFunctionProps:
    def __init__(
        self,
        *,
        basic_auth_string: builtins.str,
        exclude_paths: typing.Optional[typing.Sequence[typing.Union[NaiveBasicAuthCloudfrontFunctionExcludedPath, typing.Dict[builtins.str, typing.Any]]]] = None,
    ) -> None:
        '''(experimental) Props for the NaiveBasicAuthCloudfrontFunction construct.

        :param basic_auth_string: (experimental) The basic auth string to use for checking basic auth credentials You can generate a basic auth string using the following command: echo -n "$username:$password" | base64.
        :param exclude_paths: (experimental) The paths to exclude from basic auth. Pass a string or regex to match the path. Strings are checked using === operator. Default: - no paths are excluded

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__35170ecaf31393ae4e535e7b932855526964579db38be7b84aa1931339ceea19)
            check_type(argname="argument basic_auth_string", value=basic_auth_string, expected_type=type_hints["basic_auth_string"])
            check_type(argname="argument exclude_paths", value=exclude_paths, expected_type=type_hints["exclude_paths"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "basic_auth_string": basic_auth_string,
        }
        if exclude_paths is not None:
            self._values["exclude_paths"] = exclude_paths

    @builtins.property
    def basic_auth_string(self) -> builtins.str:
        '''(experimental) The basic auth string to use for checking basic auth credentials You can generate a basic auth string using the following command: echo -n "$username:$password" | base64.

        :stability: experimental
        '''
        result = self._values.get("basic_auth_string")
        assert result is not None, "Required property 'basic_auth_string' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def exclude_paths(
        self,
    ) -> typing.Optional[typing.List[NaiveBasicAuthCloudfrontFunctionExcludedPath]]:
        '''(experimental) The paths to exclude from basic auth.

        Pass a string or regex to match the path. Strings are checked using === operator.

        :default: - no paths are excluded

        :stability: experimental
        '''
        result = self._values.get("exclude_paths")
        return typing.cast(typing.Optional[typing.List[NaiveBasicAuthCloudfrontFunctionExcludedPath]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NaiveBasicAuthCloudfrontFunctionProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(INetworking)
class Networking(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@condensetech/cdk-constructs.Networking",
):
    '''(experimental) The Networking construct creates a VPC which can have public, private, and isolated subnets.

    It enforces to define a CIDR block for the VPC, which is a best practice.

    If the ``natGateways`` property is set to a positive integer, the VPC will be created with private subnets that have access to the internet through NAT gateways.
    If instead the ``natGateways`` property is set to 0, the VPC will have only public and isolated subnets. In this case, the subnets will anyway use a cidrMask of ``24``, so that changing the number of NAT gateways will not require to re-provision the VPC.

    In addition, this construct can also take care of creating a bastion host in the VPC by using the latest Amazon Linux AMI with the smallest available instance (t4g.nano), if the ``bastionHostEnabled`` property is set to ``true``.

    :stability: experimental
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        ip_addresses: _aws_cdk_aws_ec2_ceddda9d.IIpAddresses,
        bastion_host_ami: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IMachineImage] = None,
        bastion_host_enabled: typing.Optional[builtins.bool] = None,
        bastion_host_instance_type: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.InstanceType] = None,
        bastion_name: typing.Optional[builtins.str] = None,
        max_azs: typing.Optional[jsii.Number] = None,
        nat_gateways: typing.Optional[jsii.Number] = None,
        vpc_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param ip_addresses: 
        :param bastion_host_ami: 
        :param bastion_host_enabled: 
        :param bastion_host_instance_type: 
        :param bastion_name: 
        :param max_azs: 
        :param nat_gateways: 
        :param vpc_name: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9333f69a8b9c318ec7120273e8700bfc06f052d41e91c864702225cd0e11efdb)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = NetworkingProps(
            ip_addresses=ip_addresses,
            bastion_host_ami=bastion_host_ami,
            bastion_host_enabled=bastion_host_enabled,
            bastion_host_instance_type=bastion_host_instance_type,
            bastion_name=bastion_name,
            max_azs=max_azs,
            nat_gateways=nat_gateways,
            vpc_name=vpc_name,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property
    @jsii.member(jsii_name="hasPrivateSubnets")
    def has_private_subnets(self) -> builtins.bool:
        '''(experimental) Returns if the VPC has private subnets (with access to internet through a NAT gateway).

        :stability: experimental
        '''
        return typing.cast(builtins.bool, jsii.get(self, "hasPrivateSubnets"))

    @builtins.property
    @jsii.member(jsii_name="isolatedSubnets")
    def isolated_subnets(self) -> _aws_cdk_aws_ec2_ceddda9d.SubnetSelection:
        '''(experimental) Returns the isolated subnets of the VPC (without access to internet).

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, jsii.get(self, "isolatedSubnets"))

    @builtins.property
    @jsii.member(jsii_name="publicSubnets")
    def public_subnets(self) -> _aws_cdk_aws_ec2_ceddda9d.SubnetSelection:
        '''(experimental) Returns the public subnets of the VPC.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, jsii.get(self, "publicSubnets"))

    @builtins.property
    @jsii.member(jsii_name="vpc")
    def vpc(self) -> _aws_cdk_aws_ec2_ceddda9d.IVpc:
        '''(experimental) The VPC where the networking resources are created.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.IVpc, jsii.get(self, "vpc"))

    @builtins.property
    @jsii.member(jsii_name="bastionHost")
    def bastion_host(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IConnectable]:
        '''(experimental) Returns the bastion host instance of the VPC, if any.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IConnectable], jsii.get(self, "bastionHost"))

    @builtins.property
    @jsii.member(jsii_name="privateSubnets")
    def private_subnets(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection]:
        '''(experimental) Returns the private subnets of the VPC (with access to internet through a NAT gateway).

        :stability: experimental
        '''
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection], jsii.get(self, "privateSubnets"))


@jsii.data_type(
    jsii_type="@condensetech/cdk-constructs.NetworkingProps",
    jsii_struct_bases=[],
    name_mapping={
        "ip_addresses": "ipAddresses",
        "bastion_host_ami": "bastionHostAmi",
        "bastion_host_enabled": "bastionHostEnabled",
        "bastion_host_instance_type": "bastionHostInstanceType",
        "bastion_name": "bastionName",
        "max_azs": "maxAzs",
        "nat_gateways": "natGateways",
        "vpc_name": "vpcName",
    },
)
class NetworkingProps:
    def __init__(
        self,
        *,
        ip_addresses: _aws_cdk_aws_ec2_ceddda9d.IIpAddresses,
        bastion_host_ami: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IMachineImage] = None,
        bastion_host_enabled: typing.Optional[builtins.bool] = None,
        bastion_host_instance_type: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.InstanceType] = None,
        bastion_name: typing.Optional[builtins.str] = None,
        max_azs: typing.Optional[jsii.Number] = None,
        nat_gateways: typing.Optional[jsii.Number] = None,
        vpc_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Properties for the Networking construct.

        :param ip_addresses: 
        :param bastion_host_ami: 
        :param bastion_host_enabled: 
        :param bastion_host_instance_type: 
        :param bastion_name: 
        :param max_azs: 
        :param nat_gateways: 
        :param vpc_name: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__76cefbe0036052e6c98f7dd510a4c421bbbf507fe910b749b221863b80be96ab)
            check_type(argname="argument ip_addresses", value=ip_addresses, expected_type=type_hints["ip_addresses"])
            check_type(argname="argument bastion_host_ami", value=bastion_host_ami, expected_type=type_hints["bastion_host_ami"])
            check_type(argname="argument bastion_host_enabled", value=bastion_host_enabled, expected_type=type_hints["bastion_host_enabled"])
            check_type(argname="argument bastion_host_instance_type", value=bastion_host_instance_type, expected_type=type_hints["bastion_host_instance_type"])
            check_type(argname="argument bastion_name", value=bastion_name, expected_type=type_hints["bastion_name"])
            check_type(argname="argument max_azs", value=max_azs, expected_type=type_hints["max_azs"])
            check_type(argname="argument nat_gateways", value=nat_gateways, expected_type=type_hints["nat_gateways"])
            check_type(argname="argument vpc_name", value=vpc_name, expected_type=type_hints["vpc_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "ip_addresses": ip_addresses,
        }
        if bastion_host_ami is not None:
            self._values["bastion_host_ami"] = bastion_host_ami
        if bastion_host_enabled is not None:
            self._values["bastion_host_enabled"] = bastion_host_enabled
        if bastion_host_instance_type is not None:
            self._values["bastion_host_instance_type"] = bastion_host_instance_type
        if bastion_name is not None:
            self._values["bastion_name"] = bastion_name
        if max_azs is not None:
            self._values["max_azs"] = max_azs
        if nat_gateways is not None:
            self._values["nat_gateways"] = nat_gateways
        if vpc_name is not None:
            self._values["vpc_name"] = vpc_name

    @builtins.property
    def ip_addresses(self) -> _aws_cdk_aws_ec2_ceddda9d.IIpAddresses:
        '''
        :stability: experimental
        '''
        result = self._values.get("ip_addresses")
        assert result is not None, "Required property 'ip_addresses' is missing"
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.IIpAddresses, result)

    @builtins.property
    def bastion_host_ami(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IMachineImage]:
        '''
        :stability: experimental
        '''
        result = self._values.get("bastion_host_ami")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IMachineImage], result)

    @builtins.property
    def bastion_host_enabled(self) -> typing.Optional[builtins.bool]:
        '''
        :stability: experimental
        '''
        result = self._values.get("bastion_host_enabled")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def bastion_host_instance_type(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.InstanceType]:
        '''
        :stability: experimental
        '''
        result = self._values.get("bastion_host_instance_type")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.InstanceType], result)

    @builtins.property
    def bastion_name(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("bastion_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def max_azs(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("max_azs")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def nat_gateways(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("nat_gateways")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def vpc_name(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("vpc_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NetworkingProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(INetworking)
class NetworkingStack(
    _aws_cdk_ceddda9d.Stack,
    metaclass=jsii.JSIIMeta,
    jsii_type="@condensetech/cdk-constructs.NetworkingStack",
):
    '''(experimental) The NetworkingStack creates a `Networking <#@condensetech/cdk-constructs.Networking>`_ construct. It implements the INetworking interface so that it can be used in other constructs and stacks without requiring to access to the underlying construct.

    :stability: experimental
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        ip_addresses: _aws_cdk_aws_ec2_ceddda9d.IIpAddresses,
        bastion_host_ami: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IMachineImage] = None,
        bastion_host_enabled: typing.Optional[builtins.bool] = None,
        bastion_host_instance_type: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.InstanceType] = None,
        bastion_name: typing.Optional[builtins.str] = None,
        max_azs: typing.Optional[jsii.Number] = None,
        nat_gateways: typing.Optional[jsii.Number] = None,
        vpc_name: typing.Optional[builtins.str] = None,
        analytics_reporting: typing.Optional[builtins.bool] = None,
        cross_region_references: typing.Optional[builtins.bool] = None,
        description: typing.Optional[builtins.str] = None,
        env: typing.Optional[typing.Union[_aws_cdk_ceddda9d.Environment, typing.Dict[builtins.str, typing.Any]]] = None,
        permissions_boundary: typing.Optional[_aws_cdk_ceddda9d.PermissionsBoundary] = None,
        stack_name: typing.Optional[builtins.str] = None,
        suppress_template_indentation: typing.Optional[builtins.bool] = None,
        synthesizer: typing.Optional[_aws_cdk_ceddda9d.IStackSynthesizer] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        termination_protection: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param ip_addresses: 
        :param bastion_host_ami: 
        :param bastion_host_enabled: 
        :param bastion_host_instance_type: 
        :param bastion_name: 
        :param max_azs: 
        :param nat_gateways: 
        :param vpc_name: 
        :param analytics_reporting: Include runtime versioning information in this Stack. Default: ``analyticsReporting`` setting of containing ``App``, or value of 'aws:cdk:version-reporting' context key
        :param cross_region_references: Enable this flag to allow native cross region stack references. Enabling this will create a CloudFormation custom resource in both the producing stack and consuming stack in order to perform the export/import This feature is currently experimental Default: false
        :param description: A description of the stack. Default: - No description.
        :param env: The AWS environment (account/region) where this stack will be deployed. Set the ``region``/``account`` fields of ``env`` to either a concrete value to select the indicated environment (recommended for production stacks), or to the values of environment variables ``CDK_DEFAULT_REGION``/``CDK_DEFAULT_ACCOUNT`` to let the target environment depend on the AWS credentials/configuration that the CDK CLI is executed under (recommended for development stacks). If the ``Stack`` is instantiated inside a ``Stage``, any undefined ``region``/``account`` fields from ``env`` will default to the same field on the encompassing ``Stage``, if configured there. If either ``region`` or ``account`` are not set nor inherited from ``Stage``, the Stack will be considered "*environment-agnostic*"". Environment-agnostic stacks can be deployed to any environment but may not be able to take advantage of all features of the CDK. For example, they will not be able to use environmental context lookups such as ``ec2.Vpc.fromLookup`` and will not automatically translate Service Principals to the right format based on the environment's AWS partition, and other such enhancements. Default: - The environment of the containing ``Stage`` if available, otherwise create the stack will be environment-agnostic.
        :param permissions_boundary: Options for applying a permissions boundary to all IAM Roles and Users created within this Stage. Default: - no permissions boundary is applied
        :param stack_name: Name to deploy the stack with. Default: - Derived from construct path.
        :param suppress_template_indentation: Enable this flag to suppress indentation in generated CloudFormation templates. If not specified, the value of the ``@aws-cdk/core:suppressTemplateIndentation`` context key will be used. If that is not specified, then the default value ``false`` will be used. Default: - the value of ``@aws-cdk/core:suppressTemplateIndentation``, or ``false`` if that is not set.
        :param synthesizer: Synthesis method to use while deploying this stack. The Stack Synthesizer controls aspects of synthesis and deployment, like how assets are referenced and what IAM roles to use. For more information, see the README of the main CDK package. If not specified, the ``defaultStackSynthesizer`` from ``App`` will be used. If that is not specified, ``DefaultStackSynthesizer`` is used if ``@aws-cdk/core:newStyleStackSynthesis`` is set to ``true`` or the CDK major version is v2. In CDK v1 ``LegacyStackSynthesizer`` is the default if no other synthesizer is specified. Default: - The synthesizer specified on ``App``, or ``DefaultStackSynthesizer`` otherwise.
        :param tags: Stack tags that will be applied to all the taggable resources and the stack itself. Default: {}
        :param termination_protection: Whether to enable termination protection for this stack. Default: false

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3a3f5da197e1af45028448ba5f94d78977c95ec2ad500d29b674d835d5c6a638)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = NetworkingStackProps(
            ip_addresses=ip_addresses,
            bastion_host_ami=bastion_host_ami,
            bastion_host_enabled=bastion_host_enabled,
            bastion_host_instance_type=bastion_host_instance_type,
            bastion_name=bastion_name,
            max_azs=max_azs,
            nat_gateways=nat_gateways,
            vpc_name=vpc_name,
            analytics_reporting=analytics_reporting,
            cross_region_references=cross_region_references,
            description=description,
            env=env,
            permissions_boundary=permissions_boundary,
            stack_name=stack_name,
            suppress_template_indentation=suppress_template_indentation,
            synthesizer=synthesizer,
            tags=tags,
            termination_protection=termination_protection,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property
    @jsii.member(jsii_name="hasPrivateSubnets")
    def has_private_subnets(self) -> builtins.bool:
        '''(experimental) Returns if the VPC has private subnets (with access to internet through a NAT gateway).

        :stability: experimental
        '''
        return typing.cast(builtins.bool, jsii.get(self, "hasPrivateSubnets"))

    @builtins.property
    @jsii.member(jsii_name="isolatedSubnets")
    def isolated_subnets(self) -> _aws_cdk_aws_ec2_ceddda9d.SubnetSelection:
        '''(experimental) Returns the isolated subnets of the VPC (without access to internet).

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, jsii.get(self, "isolatedSubnets"))

    @builtins.property
    @jsii.member(jsii_name="publicSubnets")
    def public_subnets(self) -> _aws_cdk_aws_ec2_ceddda9d.SubnetSelection:
        '''(experimental) Returns the public subnets of the VPC.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, jsii.get(self, "publicSubnets"))

    @builtins.property
    @jsii.member(jsii_name="vpc")
    def vpc(self) -> _aws_cdk_aws_ec2_ceddda9d.IVpc:
        '''(experimental) The VPC where the networking resources are created.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.IVpc, jsii.get(self, "vpc"))

    @builtins.property
    @jsii.member(jsii_name="bastionHost")
    def bastion_host(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IConnectable]:
        '''(experimental) Returns the bastion host instance of the VPC, if any.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IConnectable], jsii.get(self, "bastionHost"))

    @builtins.property
    @jsii.member(jsii_name="privateSubnets")
    def private_subnets(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection]:
        '''(experimental) Returns the private subnets of the VPC (with access to internet through a NAT gateway).

        :stability: experimental
        '''
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection], jsii.get(self, "privateSubnets"))


@jsii.data_type(
    jsii_type="@condensetech/cdk-constructs.NetworkingStackProps",
    jsii_struct_bases=[NetworkingProps, _aws_cdk_ceddda9d.StackProps],
    name_mapping={
        "ip_addresses": "ipAddresses",
        "bastion_host_ami": "bastionHostAmi",
        "bastion_host_enabled": "bastionHostEnabled",
        "bastion_host_instance_type": "bastionHostInstanceType",
        "bastion_name": "bastionName",
        "max_azs": "maxAzs",
        "nat_gateways": "natGateways",
        "vpc_name": "vpcName",
        "analytics_reporting": "analyticsReporting",
        "cross_region_references": "crossRegionReferences",
        "description": "description",
        "env": "env",
        "permissions_boundary": "permissionsBoundary",
        "stack_name": "stackName",
        "suppress_template_indentation": "suppressTemplateIndentation",
        "synthesizer": "synthesizer",
        "tags": "tags",
        "termination_protection": "terminationProtection",
    },
)
class NetworkingStackProps(NetworkingProps, _aws_cdk_ceddda9d.StackProps):
    def __init__(
        self,
        *,
        ip_addresses: _aws_cdk_aws_ec2_ceddda9d.IIpAddresses,
        bastion_host_ami: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IMachineImage] = None,
        bastion_host_enabled: typing.Optional[builtins.bool] = None,
        bastion_host_instance_type: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.InstanceType] = None,
        bastion_name: typing.Optional[builtins.str] = None,
        max_azs: typing.Optional[jsii.Number] = None,
        nat_gateways: typing.Optional[jsii.Number] = None,
        vpc_name: typing.Optional[builtins.str] = None,
        analytics_reporting: typing.Optional[builtins.bool] = None,
        cross_region_references: typing.Optional[builtins.bool] = None,
        description: typing.Optional[builtins.str] = None,
        env: typing.Optional[typing.Union[_aws_cdk_ceddda9d.Environment, typing.Dict[builtins.str, typing.Any]]] = None,
        permissions_boundary: typing.Optional[_aws_cdk_ceddda9d.PermissionsBoundary] = None,
        stack_name: typing.Optional[builtins.str] = None,
        suppress_template_indentation: typing.Optional[builtins.bool] = None,
        synthesizer: typing.Optional[_aws_cdk_ceddda9d.IStackSynthesizer] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        termination_protection: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''(experimental) Properties for the NetworkingStack.

        :param ip_addresses: 
        :param bastion_host_ami: 
        :param bastion_host_enabled: 
        :param bastion_host_instance_type: 
        :param bastion_name: 
        :param max_azs: 
        :param nat_gateways: 
        :param vpc_name: 
        :param analytics_reporting: Include runtime versioning information in this Stack. Default: ``analyticsReporting`` setting of containing ``App``, or value of 'aws:cdk:version-reporting' context key
        :param cross_region_references: Enable this flag to allow native cross region stack references. Enabling this will create a CloudFormation custom resource in both the producing stack and consuming stack in order to perform the export/import This feature is currently experimental Default: false
        :param description: A description of the stack. Default: - No description.
        :param env: The AWS environment (account/region) where this stack will be deployed. Set the ``region``/``account`` fields of ``env`` to either a concrete value to select the indicated environment (recommended for production stacks), or to the values of environment variables ``CDK_DEFAULT_REGION``/``CDK_DEFAULT_ACCOUNT`` to let the target environment depend on the AWS credentials/configuration that the CDK CLI is executed under (recommended for development stacks). If the ``Stack`` is instantiated inside a ``Stage``, any undefined ``region``/``account`` fields from ``env`` will default to the same field on the encompassing ``Stage``, if configured there. If either ``region`` or ``account`` are not set nor inherited from ``Stage``, the Stack will be considered "*environment-agnostic*"". Environment-agnostic stacks can be deployed to any environment but may not be able to take advantage of all features of the CDK. For example, they will not be able to use environmental context lookups such as ``ec2.Vpc.fromLookup`` and will not automatically translate Service Principals to the right format based on the environment's AWS partition, and other such enhancements. Default: - The environment of the containing ``Stage`` if available, otherwise create the stack will be environment-agnostic.
        :param permissions_boundary: Options for applying a permissions boundary to all IAM Roles and Users created within this Stage. Default: - no permissions boundary is applied
        :param stack_name: Name to deploy the stack with. Default: - Derived from construct path.
        :param suppress_template_indentation: Enable this flag to suppress indentation in generated CloudFormation templates. If not specified, the value of the ``@aws-cdk/core:suppressTemplateIndentation`` context key will be used. If that is not specified, then the default value ``false`` will be used. Default: - the value of ``@aws-cdk/core:suppressTemplateIndentation``, or ``false`` if that is not set.
        :param synthesizer: Synthesis method to use while deploying this stack. The Stack Synthesizer controls aspects of synthesis and deployment, like how assets are referenced and what IAM roles to use. For more information, see the README of the main CDK package. If not specified, the ``defaultStackSynthesizer`` from ``App`` will be used. If that is not specified, ``DefaultStackSynthesizer`` is used if ``@aws-cdk/core:newStyleStackSynthesis`` is set to ``true`` or the CDK major version is v2. In CDK v1 ``LegacyStackSynthesizer`` is the default if no other synthesizer is specified. Default: - The synthesizer specified on ``App``, or ``DefaultStackSynthesizer`` otherwise.
        :param tags: Stack tags that will be applied to all the taggable resources and the stack itself. Default: {}
        :param termination_protection: Whether to enable termination protection for this stack. Default: false

        :stability: experimental
        '''
        if isinstance(env, dict):
            env = _aws_cdk_ceddda9d.Environment(**env)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0b485658e30a4cd992bcabfcfa062a6820180ada5dd60554fa23d944cee8f6f3)
            check_type(argname="argument ip_addresses", value=ip_addresses, expected_type=type_hints["ip_addresses"])
            check_type(argname="argument bastion_host_ami", value=bastion_host_ami, expected_type=type_hints["bastion_host_ami"])
            check_type(argname="argument bastion_host_enabled", value=bastion_host_enabled, expected_type=type_hints["bastion_host_enabled"])
            check_type(argname="argument bastion_host_instance_type", value=bastion_host_instance_type, expected_type=type_hints["bastion_host_instance_type"])
            check_type(argname="argument bastion_name", value=bastion_name, expected_type=type_hints["bastion_name"])
            check_type(argname="argument max_azs", value=max_azs, expected_type=type_hints["max_azs"])
            check_type(argname="argument nat_gateways", value=nat_gateways, expected_type=type_hints["nat_gateways"])
            check_type(argname="argument vpc_name", value=vpc_name, expected_type=type_hints["vpc_name"])
            check_type(argname="argument analytics_reporting", value=analytics_reporting, expected_type=type_hints["analytics_reporting"])
            check_type(argname="argument cross_region_references", value=cross_region_references, expected_type=type_hints["cross_region_references"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument env", value=env, expected_type=type_hints["env"])
            check_type(argname="argument permissions_boundary", value=permissions_boundary, expected_type=type_hints["permissions_boundary"])
            check_type(argname="argument stack_name", value=stack_name, expected_type=type_hints["stack_name"])
            check_type(argname="argument suppress_template_indentation", value=suppress_template_indentation, expected_type=type_hints["suppress_template_indentation"])
            check_type(argname="argument synthesizer", value=synthesizer, expected_type=type_hints["synthesizer"])
            check_type(argname="argument tags", value=tags, expected_type=type_hints["tags"])
            check_type(argname="argument termination_protection", value=termination_protection, expected_type=type_hints["termination_protection"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "ip_addresses": ip_addresses,
        }
        if bastion_host_ami is not None:
            self._values["bastion_host_ami"] = bastion_host_ami
        if bastion_host_enabled is not None:
            self._values["bastion_host_enabled"] = bastion_host_enabled
        if bastion_host_instance_type is not None:
            self._values["bastion_host_instance_type"] = bastion_host_instance_type
        if bastion_name is not None:
            self._values["bastion_name"] = bastion_name
        if max_azs is not None:
            self._values["max_azs"] = max_azs
        if nat_gateways is not None:
            self._values["nat_gateways"] = nat_gateways
        if vpc_name is not None:
            self._values["vpc_name"] = vpc_name
        if analytics_reporting is not None:
            self._values["analytics_reporting"] = analytics_reporting
        if cross_region_references is not None:
            self._values["cross_region_references"] = cross_region_references
        if description is not None:
            self._values["description"] = description
        if env is not None:
            self._values["env"] = env
        if permissions_boundary is not None:
            self._values["permissions_boundary"] = permissions_boundary
        if stack_name is not None:
            self._values["stack_name"] = stack_name
        if suppress_template_indentation is not None:
            self._values["suppress_template_indentation"] = suppress_template_indentation
        if synthesizer is not None:
            self._values["synthesizer"] = synthesizer
        if tags is not None:
            self._values["tags"] = tags
        if termination_protection is not None:
            self._values["termination_protection"] = termination_protection

    @builtins.property
    def ip_addresses(self) -> _aws_cdk_aws_ec2_ceddda9d.IIpAddresses:
        '''
        :stability: experimental
        '''
        result = self._values.get("ip_addresses")
        assert result is not None, "Required property 'ip_addresses' is missing"
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.IIpAddresses, result)

    @builtins.property
    def bastion_host_ami(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IMachineImage]:
        '''
        :stability: experimental
        '''
        result = self._values.get("bastion_host_ami")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IMachineImage], result)

    @builtins.property
    def bastion_host_enabled(self) -> typing.Optional[builtins.bool]:
        '''
        :stability: experimental
        '''
        result = self._values.get("bastion_host_enabled")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def bastion_host_instance_type(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.InstanceType]:
        '''
        :stability: experimental
        '''
        result = self._values.get("bastion_host_instance_type")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.InstanceType], result)

    @builtins.property
    def bastion_name(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("bastion_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def max_azs(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("max_azs")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def nat_gateways(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("nat_gateways")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def vpc_name(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("vpc_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def analytics_reporting(self) -> typing.Optional[builtins.bool]:
        '''Include runtime versioning information in this Stack.

        :default:

        ``analyticsReporting`` setting of containing ``App``, or value of
        'aws:cdk:version-reporting' context key
        '''
        result = self._values.get("analytics_reporting")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def cross_region_references(self) -> typing.Optional[builtins.bool]:
        '''Enable this flag to allow native cross region stack references.

        Enabling this will create a CloudFormation custom resource
        in both the producing stack and consuming stack in order to perform the export/import

        This feature is currently experimental

        :default: false
        '''
        result = self._values.get("cross_region_references")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''A description of the stack.

        :default: - No description.
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def env(self) -> typing.Optional[_aws_cdk_ceddda9d.Environment]:
        '''The AWS environment (account/region) where this stack will be deployed.

        Set the ``region``/``account`` fields of ``env`` to either a concrete value to
        select the indicated environment (recommended for production stacks), or to
        the values of environment variables
        ``CDK_DEFAULT_REGION``/``CDK_DEFAULT_ACCOUNT`` to let the target environment
        depend on the AWS credentials/configuration that the CDK CLI is executed
        under (recommended for development stacks).

        If the ``Stack`` is instantiated inside a ``Stage``, any undefined
        ``region``/``account`` fields from ``env`` will default to the same field on the
        encompassing ``Stage``, if configured there.

        If either ``region`` or ``account`` are not set nor inherited from ``Stage``, the
        Stack will be considered "*environment-agnostic*"". Environment-agnostic
        stacks can be deployed to any environment but may not be able to take
        advantage of all features of the CDK. For example, they will not be able to
        use environmental context lookups such as ``ec2.Vpc.fromLookup`` and will not
        automatically translate Service Principals to the right format based on the
        environment's AWS partition, and other such enhancements.

        :default:

        - The environment of the containing ``Stage`` if available,
        otherwise create the stack will be environment-agnostic.

        Example::

            // Use a concrete account and region to deploy this stack to:
            // `.account` and `.region` will simply return these values.
            new Stack(app, 'Stack1', {
              env: {
                account: '123456789012',
                region: 'us-east-1'
              },
            });
            
            // Use the CLI's current credentials to determine the target environment:
            // `.account` and `.region` will reflect the account+region the CLI
            // is configured to use (based on the user CLI credentials)
            new Stack(app, 'Stack2', {
              env: {
                account: process.env.CDK_DEFAULT_ACCOUNT,
                region: process.env.CDK_DEFAULT_REGION
              },
            });
            
            // Define multiple stacks stage associated with an environment
            const myStage = new Stage(app, 'MyStage', {
              env: {
                account: '123456789012',
                region: 'us-east-1'
              }
            });
            
            // both of these stacks will use the stage's account/region:
            // `.account` and `.region` will resolve to the concrete values as above
            new MyStack(myStage, 'Stack1');
            new YourStack(myStage, 'Stack2');
            
            // Define an environment-agnostic stack:
            // `.account` and `.region` will resolve to `{ "Ref": "AWS::AccountId" }` and `{ "Ref": "AWS::Region" }` respectively.
            // which will only resolve to actual values by CloudFormation during deployment.
            new MyStack(app, 'Stack1');
        '''
        result = self._values.get("env")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Environment], result)

    @builtins.property
    def permissions_boundary(
        self,
    ) -> typing.Optional[_aws_cdk_ceddda9d.PermissionsBoundary]:
        '''Options for applying a permissions boundary to all IAM Roles and Users created within this Stage.

        :default: - no permissions boundary is applied
        '''
        result = self._values.get("permissions_boundary")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.PermissionsBoundary], result)

    @builtins.property
    def stack_name(self) -> typing.Optional[builtins.str]:
        '''Name to deploy the stack with.

        :default: - Derived from construct path.
        '''
        result = self._values.get("stack_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def suppress_template_indentation(self) -> typing.Optional[builtins.bool]:
        '''Enable this flag to suppress indentation in generated CloudFormation templates.

        If not specified, the value of the ``@aws-cdk/core:suppressTemplateIndentation``
        context key will be used. If that is not specified, then the
        default value ``false`` will be used.

        :default: - the value of ``@aws-cdk/core:suppressTemplateIndentation``, or ``false`` if that is not set.
        '''
        result = self._values.get("suppress_template_indentation")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def synthesizer(self) -> typing.Optional[_aws_cdk_ceddda9d.IStackSynthesizer]:
        '''Synthesis method to use while deploying this stack.

        The Stack Synthesizer controls aspects of synthesis and deployment,
        like how assets are referenced and what IAM roles to use. For more
        information, see the README of the main CDK package.

        If not specified, the ``defaultStackSynthesizer`` from ``App`` will be used.
        If that is not specified, ``DefaultStackSynthesizer`` is used if
        ``@aws-cdk/core:newStyleStackSynthesis`` is set to ``true`` or the CDK major
        version is v2. In CDK v1 ``LegacyStackSynthesizer`` is the default if no
        other synthesizer is specified.

        :default: - The synthesizer specified on ``App``, or ``DefaultStackSynthesizer`` otherwise.
        '''
        result = self._values.get("synthesizer")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.IStackSynthesizer], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Stack tags that will be applied to all the taggable resources and the stack itself.

        :default: {}
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def termination_protection(self) -> typing.Optional[builtins.bool]:
        '''Whether to enable termination protection for this stack.

        :default: false
        '''
        result = self._values.get("termination_protection")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NetworkingStackProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(_aws_cdk_ceddda9d.IAspect)
class RdsClusterMonitoringAspect(
    metaclass=jsii.JSIIMeta,
    jsii_type="@condensetech/cdk-constructs.RdsClusterMonitoringAspect",
):
    '''(experimental) The RdsClusterMonitoringAspect iterates over the RDS clusters and adds monitoring widgets and alarms.

    :stability: experimental
    '''

    def __init__(self, monitoring_facade: ICondenseMonitoringFacade) -> None:
        '''
        :param monitoring_facade: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4aca2c196ab1077acc3c53fe795c33684b2b614468023689c3a055c3f9b492c5)
            check_type(argname="argument monitoring_facade", value=monitoring_facade, expected_type=type_hints["monitoring_facade"])
        jsii.create(self.__class__, self, [monitoring_facade])

    @jsii.member(jsii_name="overrideConfig")
    def override_config(
        self,
        node: _aws_cdk_aws_rds_ceddda9d.DatabaseCluster,
        *,
        cpu_utilization_threshold: typing.Optional[jsii.Number] = None,
        ebs_byte_balance_threshold: typing.Optional[jsii.Number] = None,
        ebs_io_balance_threshold: typing.Optional[jsii.Number] = None,
        freeable_memory_threshold: typing.Optional[_aws_cdk_ceddda9d.Size] = None,
        max_connections_threshold: typing.Optional[jsii.Number] = None,
        read_latency_threshold: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''(experimental) Overrides the default configuration for a specific RDS cluster.

        :param node: The RDS cluster to monitor.
        :param cpu_utilization_threshold: (experimental) The CPU Utilization (%) threshold. Default: 90
        :param ebs_byte_balance_threshold: (experimental) The EBS Byte Balance (%) threshold. Default: 10
        :param ebs_io_balance_threshold: (experimental) The EBS IO Balance (%) threshold. Default: 10
        :param freeable_memory_threshold: (experimental) The Freeable Memory threshold. Default: 100 MiB
        :param max_connections_threshold: (experimental) The Max Connections threshold. Default: 50
        :param read_latency_threshold: (experimental) The Read Latency threshold. Default: 20

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a5f22f24629398f744a2a08eb4f5377bd7a3b6b6f99cc28ac4c3928736022f1d)
            check_type(argname="argument node", value=node, expected_type=type_hints["node"])
        config = RdsClusterMonitoringConfig(
            cpu_utilization_threshold=cpu_utilization_threshold,
            ebs_byte_balance_threshold=ebs_byte_balance_threshold,
            ebs_io_balance_threshold=ebs_io_balance_threshold,
            freeable_memory_threshold=freeable_memory_threshold,
            max_connections_threshold=max_connections_threshold,
            read_latency_threshold=read_latency_threshold,
        )

        return typing.cast(None, jsii.invoke(self, "overrideConfig", [node, config]))

    @jsii.member(jsii_name="visit")
    def visit(self, node: _constructs_77d1e7e8.IConstruct) -> None:
        '''(experimental) All aspects can visit an IConstruct.

        :param node: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__20d91c6ae5b029b42be80d506f3b6044ae0bf016b7daa8e33d8c6d4b0143c20b)
            check_type(argname="argument node", value=node, expected_type=type_hints["node"])
        return typing.cast(None, jsii.invoke(self, "visit", [node]))


@jsii.data_type(
    jsii_type="@condensetech/cdk-constructs.RdsClusterMonitoringConfig",
    jsii_struct_bases=[],
    name_mapping={
        "cpu_utilization_threshold": "cpuUtilizationThreshold",
        "ebs_byte_balance_threshold": "ebsByteBalanceThreshold",
        "ebs_io_balance_threshold": "ebsIoBalanceThreshold",
        "freeable_memory_threshold": "freeableMemoryThreshold",
        "max_connections_threshold": "maxConnectionsThreshold",
        "read_latency_threshold": "readLatencyThreshold",
    },
)
class RdsClusterMonitoringConfig:
    def __init__(
        self,
        *,
        cpu_utilization_threshold: typing.Optional[jsii.Number] = None,
        ebs_byte_balance_threshold: typing.Optional[jsii.Number] = None,
        ebs_io_balance_threshold: typing.Optional[jsii.Number] = None,
        freeable_memory_threshold: typing.Optional[_aws_cdk_ceddda9d.Size] = None,
        max_connections_threshold: typing.Optional[jsii.Number] = None,
        read_latency_threshold: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''(experimental) The RdsClusterMonitoringConfig defines the thresholds for the RDS cluster monitoring.

        :param cpu_utilization_threshold: (experimental) The CPU Utilization (%) threshold. Default: 90
        :param ebs_byte_balance_threshold: (experimental) The EBS Byte Balance (%) threshold. Default: 10
        :param ebs_io_balance_threshold: (experimental) The EBS IO Balance (%) threshold. Default: 10
        :param freeable_memory_threshold: (experimental) The Freeable Memory threshold. Default: 100 MiB
        :param max_connections_threshold: (experimental) The Max Connections threshold. Default: 50
        :param read_latency_threshold: (experimental) The Read Latency threshold. Default: 20

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__eca8553b2bbcadedc0bc66ed7c18f8470da2dc0dc250714df2eda482318e71ea)
            check_type(argname="argument cpu_utilization_threshold", value=cpu_utilization_threshold, expected_type=type_hints["cpu_utilization_threshold"])
            check_type(argname="argument ebs_byte_balance_threshold", value=ebs_byte_balance_threshold, expected_type=type_hints["ebs_byte_balance_threshold"])
            check_type(argname="argument ebs_io_balance_threshold", value=ebs_io_balance_threshold, expected_type=type_hints["ebs_io_balance_threshold"])
            check_type(argname="argument freeable_memory_threshold", value=freeable_memory_threshold, expected_type=type_hints["freeable_memory_threshold"])
            check_type(argname="argument max_connections_threshold", value=max_connections_threshold, expected_type=type_hints["max_connections_threshold"])
            check_type(argname="argument read_latency_threshold", value=read_latency_threshold, expected_type=type_hints["read_latency_threshold"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if cpu_utilization_threshold is not None:
            self._values["cpu_utilization_threshold"] = cpu_utilization_threshold
        if ebs_byte_balance_threshold is not None:
            self._values["ebs_byte_balance_threshold"] = ebs_byte_balance_threshold
        if ebs_io_balance_threshold is not None:
            self._values["ebs_io_balance_threshold"] = ebs_io_balance_threshold
        if freeable_memory_threshold is not None:
            self._values["freeable_memory_threshold"] = freeable_memory_threshold
        if max_connections_threshold is not None:
            self._values["max_connections_threshold"] = max_connections_threshold
        if read_latency_threshold is not None:
            self._values["read_latency_threshold"] = read_latency_threshold

    @builtins.property
    def cpu_utilization_threshold(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The CPU Utilization (%) threshold.

        :default: 90

        :stability: experimental
        '''
        result = self._values.get("cpu_utilization_threshold")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def ebs_byte_balance_threshold(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The EBS Byte Balance (%) threshold.

        :default: 10

        :stability: experimental
        '''
        result = self._values.get("ebs_byte_balance_threshold")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def ebs_io_balance_threshold(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The EBS IO Balance (%) threshold.

        :default: 10

        :stability: experimental
        '''
        result = self._values.get("ebs_io_balance_threshold")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def freeable_memory_threshold(self) -> typing.Optional[_aws_cdk_ceddda9d.Size]:
        '''(experimental) The Freeable Memory threshold.

        :default: 100 MiB

        :stability: experimental
        '''
        result = self._values.get("freeable_memory_threshold")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Size], result)

    @builtins.property
    def max_connections_threshold(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The Max Connections threshold.

        :default: 50

        :stability: experimental
        '''
        result = self._values.get("max_connections_threshold")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def read_latency_threshold(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The Read Latency threshold.

        :default: 20

        :stability: experimental
        '''
        result = self._values.get("read_latency_threshold")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RdsClusterMonitoringConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(_aws_cdk_ceddda9d.IAspect)
class RdsInstanceMonitoringAspect(
    metaclass=jsii.JSIIMeta,
    jsii_type="@condensetech/cdk-constructs.RdsInstanceMonitoringAspect",
):
    '''(experimental) The RdsInstanceMonitoringAspect iterates over the RDS instances and adds monitoring widgets and alarms.

    :stability: experimental
    '''

    def __init__(self, monitoring_facade: ICondenseMonitoringFacade) -> None:
        '''
        :param monitoring_facade: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__93469445a9438705a1bedc45123357e71bf0034dd3957f7c851bd8caad946f2a)
            check_type(argname="argument monitoring_facade", value=monitoring_facade, expected_type=type_hints["monitoring_facade"])
        jsii.create(self.__class__, self, [monitoring_facade])

    @jsii.member(jsii_name="overrideConfig")
    def override_config(
        self,
        node: _aws_cdk_aws_rds_ceddda9d.DatabaseInstance,
        *,
        cpu_utilization_threshold: typing.Optional[jsii.Number] = None,
        ebs_byte_balance_threshold: typing.Optional[jsii.Number] = None,
        ebs_io_balance_threshold: typing.Optional[jsii.Number] = None,
        freeable_memory_threshold: typing.Optional[_aws_cdk_ceddda9d.Size] = None,
        free_storage_space_threshold: typing.Optional[_aws_cdk_ceddda9d.Size] = None,
        max_connections_threshold: typing.Optional[jsii.Number] = None,
        read_latency_threshold: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''(experimental) Overrides the default configuration for the RDS instance.

        :param node: The RDS instance to monitor.
        :param cpu_utilization_threshold: (experimental) The CPU Utilization (%) threshold. Default: 90
        :param ebs_byte_balance_threshold: (experimental) The EBS Byte Balance (%) threshold. Default: 10
        :param ebs_io_balance_threshold: (experimental) The EBS IO Balance (%) threshold. Default: 10
        :param freeable_memory_threshold: (experimental) The Freeable Memory threshold. Default: 100 MiB
        :param free_storage_space_threshold: (experimental) The Free Storage Space threshold. Default: 100 MiB
        :param max_connections_threshold: (experimental) The Max Connections threshold. Default: 50
        :param read_latency_threshold: (experimental) The Read Latency threshold. Default: 20

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bf21bc988337443e51be3192cdb0b1135c9f5c2d3b9581366b89ae59cd3ef8db)
            check_type(argname="argument node", value=node, expected_type=type_hints["node"])
        config = RdsInstanceMonitoringConfig(
            cpu_utilization_threshold=cpu_utilization_threshold,
            ebs_byte_balance_threshold=ebs_byte_balance_threshold,
            ebs_io_balance_threshold=ebs_io_balance_threshold,
            freeable_memory_threshold=freeable_memory_threshold,
            free_storage_space_threshold=free_storage_space_threshold,
            max_connections_threshold=max_connections_threshold,
            read_latency_threshold=read_latency_threshold,
        )

        return typing.cast(None, jsii.invoke(self, "overrideConfig", [node, config]))

    @jsii.member(jsii_name="visit")
    def visit(self, node: _constructs_77d1e7e8.IConstruct) -> None:
        '''(experimental) All aspects can visit an IConstruct.

        :param node: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f2d14017d7e7fd1f9ed75765544e708efbd58aeb885da78632062a5b2cd16ad0)
            check_type(argname="argument node", value=node, expected_type=type_hints["node"])
        return typing.cast(None, jsii.invoke(self, "visit", [node]))


@jsii.data_type(
    jsii_type="@condensetech/cdk-constructs.RdsInstanceMonitoringConfig",
    jsii_struct_bases=[],
    name_mapping={
        "cpu_utilization_threshold": "cpuUtilizationThreshold",
        "ebs_byte_balance_threshold": "ebsByteBalanceThreshold",
        "ebs_io_balance_threshold": "ebsIoBalanceThreshold",
        "freeable_memory_threshold": "freeableMemoryThreshold",
        "free_storage_space_threshold": "freeStorageSpaceThreshold",
        "max_connections_threshold": "maxConnectionsThreshold",
        "read_latency_threshold": "readLatencyThreshold",
    },
)
class RdsInstanceMonitoringConfig:
    def __init__(
        self,
        *,
        cpu_utilization_threshold: typing.Optional[jsii.Number] = None,
        ebs_byte_balance_threshold: typing.Optional[jsii.Number] = None,
        ebs_io_balance_threshold: typing.Optional[jsii.Number] = None,
        freeable_memory_threshold: typing.Optional[_aws_cdk_ceddda9d.Size] = None,
        free_storage_space_threshold: typing.Optional[_aws_cdk_ceddda9d.Size] = None,
        max_connections_threshold: typing.Optional[jsii.Number] = None,
        read_latency_threshold: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''(experimental) The RdsInstanceMonitoringConfig defines the thresholds for the RDS instance monitoring.

        :param cpu_utilization_threshold: (experimental) The CPU Utilization (%) threshold. Default: 90
        :param ebs_byte_balance_threshold: (experimental) The EBS Byte Balance (%) threshold. Default: 10
        :param ebs_io_balance_threshold: (experimental) The EBS IO Balance (%) threshold. Default: 10
        :param freeable_memory_threshold: (experimental) The Freeable Memory threshold. Default: 100 MiB
        :param free_storage_space_threshold: (experimental) The Free Storage Space threshold. Default: 100 MiB
        :param max_connections_threshold: (experimental) The Max Connections threshold. Default: 50
        :param read_latency_threshold: (experimental) The Read Latency threshold. Default: 20

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2d08db96b75dd7234176dfe2c64e7ae1bedc0d3bb341bb1db6375b0b1f865b05)
            check_type(argname="argument cpu_utilization_threshold", value=cpu_utilization_threshold, expected_type=type_hints["cpu_utilization_threshold"])
            check_type(argname="argument ebs_byte_balance_threshold", value=ebs_byte_balance_threshold, expected_type=type_hints["ebs_byte_balance_threshold"])
            check_type(argname="argument ebs_io_balance_threshold", value=ebs_io_balance_threshold, expected_type=type_hints["ebs_io_balance_threshold"])
            check_type(argname="argument freeable_memory_threshold", value=freeable_memory_threshold, expected_type=type_hints["freeable_memory_threshold"])
            check_type(argname="argument free_storage_space_threshold", value=free_storage_space_threshold, expected_type=type_hints["free_storage_space_threshold"])
            check_type(argname="argument max_connections_threshold", value=max_connections_threshold, expected_type=type_hints["max_connections_threshold"])
            check_type(argname="argument read_latency_threshold", value=read_latency_threshold, expected_type=type_hints["read_latency_threshold"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if cpu_utilization_threshold is not None:
            self._values["cpu_utilization_threshold"] = cpu_utilization_threshold
        if ebs_byte_balance_threshold is not None:
            self._values["ebs_byte_balance_threshold"] = ebs_byte_balance_threshold
        if ebs_io_balance_threshold is not None:
            self._values["ebs_io_balance_threshold"] = ebs_io_balance_threshold
        if freeable_memory_threshold is not None:
            self._values["freeable_memory_threshold"] = freeable_memory_threshold
        if free_storage_space_threshold is not None:
            self._values["free_storage_space_threshold"] = free_storage_space_threshold
        if max_connections_threshold is not None:
            self._values["max_connections_threshold"] = max_connections_threshold
        if read_latency_threshold is not None:
            self._values["read_latency_threshold"] = read_latency_threshold

    @builtins.property
    def cpu_utilization_threshold(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The CPU Utilization (%) threshold.

        :default: 90

        :stability: experimental
        '''
        result = self._values.get("cpu_utilization_threshold")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def ebs_byte_balance_threshold(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The EBS Byte Balance (%) threshold.

        :default: 10

        :stability: experimental
        '''
        result = self._values.get("ebs_byte_balance_threshold")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def ebs_io_balance_threshold(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The EBS IO Balance (%) threshold.

        :default: 10

        :stability: experimental
        '''
        result = self._values.get("ebs_io_balance_threshold")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def freeable_memory_threshold(self) -> typing.Optional[_aws_cdk_ceddda9d.Size]:
        '''(experimental) The Freeable Memory threshold.

        :default: 100 MiB

        :stability: experimental
        '''
        result = self._values.get("freeable_memory_threshold")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Size], result)

    @builtins.property
    def free_storage_space_threshold(self) -> typing.Optional[_aws_cdk_ceddda9d.Size]:
        '''(experimental) The Free Storage Space threshold.

        :default: 100 MiB

        :stability: experimental
        '''
        result = self._values.get("free_storage_space_threshold")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Size], result)

    @builtins.property
    def max_connections_threshold(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The Max Connections threshold.

        :default: 50

        :stability: experimental
        '''
        result = self._values.get("max_connections_threshold")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def read_latency_threshold(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The Read Latency threshold.

        :default: 20

        :stability: experimental
        '''
        result = self._values.get("read_latency_threshold")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RdsInstanceMonitoringConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(_aws_cdk_ceddda9d.IAspect)
class TargetGroupMonitoringAspect(
    metaclass=jsii.JSIIMeta,
    jsii_type="@condensetech/cdk-constructs.TargetGroupMonitoringAspect",
):
    '''(experimental) The TargetGroupMonitoringAspect iterates over the target groups and adds monitoring widgets and alarms.

    :stability: experimental
    '''

    def __init__(self, monitoring_facade: ICondenseMonitoringFacade) -> None:
        '''
        :param monitoring_facade: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__24955513de57d1b7cc9c76f39b7d30a926cd40697184c043fafc5ad4cbd9c667)
            check_type(argname="argument monitoring_facade", value=monitoring_facade, expected_type=type_hints["monitoring_facade"])
        jsii.create(self.__class__, self, [monitoring_facade])

    @jsii.member(jsii_name="overrideConfig")
    def override_config(
        self,
        node: _aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ApplicationTargetGroup,
        *,
        min_healthy_hosts_threshold: typing.Optional[jsii.Number] = None,
        response_time_threshold: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    ) -> None:
        '''(experimental) Overrides the default configuration for a specific target group.

        :param node: The target group to monitor.
        :param min_healthy_hosts_threshold: (experimental) The Min Healthy Hosts threshold. Default: 1
        :param response_time_threshold: (experimental) The Response Time threshold. Default: - No threshold.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a1b1e908a3fff25a3d0a4d7e4611154465b0d84ff11973cf045225e068bae815)
            check_type(argname="argument node", value=node, expected_type=type_hints["node"])
        config = TargetGroupMonitoringConfig(
            min_healthy_hosts_threshold=min_healthy_hosts_threshold,
            response_time_threshold=response_time_threshold,
        )

        return typing.cast(None, jsii.invoke(self, "overrideConfig", [node, config]))

    @jsii.member(jsii_name="visit")
    def visit(self, node: _constructs_77d1e7e8.IConstruct) -> None:
        '''(experimental) All aspects can visit an IConstruct.

        :param node: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3817ebef06ec180d4a607f13776609a70965bf3b9ca0e264b5d069f374321ce3)
            check_type(argname="argument node", value=node, expected_type=type_hints["node"])
        return typing.cast(None, jsii.invoke(self, "visit", [node]))

    @builtins.property
    @jsii.member(jsii_name="monitoringFacade")
    def monitoring_facade(self) -> ICondenseMonitoringFacade:
        '''
        :stability: experimental
        '''
        return typing.cast(ICondenseMonitoringFacade, jsii.get(self, "monitoringFacade"))


@jsii.data_type(
    jsii_type="@condensetech/cdk-constructs.TargetGroupMonitoringConfig",
    jsii_struct_bases=[],
    name_mapping={
        "min_healthy_hosts_threshold": "minHealthyHostsThreshold",
        "response_time_threshold": "responseTimeThreshold",
    },
)
class TargetGroupMonitoringConfig:
    def __init__(
        self,
        *,
        min_healthy_hosts_threshold: typing.Optional[jsii.Number] = None,
        response_time_threshold: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    ) -> None:
        '''(experimental) The TargetGroupMonitoringConfig defines the thresholds for the target group monitoring.

        :param min_healthy_hosts_threshold: (experimental) The Min Healthy Hosts threshold. Default: 1
        :param response_time_threshold: (experimental) The Response Time threshold. Default: - No threshold.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b0784d38b49ed7fc47c445cbd6441a0407e25d837cf3420f648b86f634b852a7)
            check_type(argname="argument min_healthy_hosts_threshold", value=min_healthy_hosts_threshold, expected_type=type_hints["min_healthy_hosts_threshold"])
            check_type(argname="argument response_time_threshold", value=response_time_threshold, expected_type=type_hints["response_time_threshold"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if min_healthy_hosts_threshold is not None:
            self._values["min_healthy_hosts_threshold"] = min_healthy_hosts_threshold
        if response_time_threshold is not None:
            self._values["response_time_threshold"] = response_time_threshold

    @builtins.property
    def min_healthy_hosts_threshold(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The Min Healthy Hosts threshold.

        :default: 1

        :stability: experimental
        '''
        result = self._values.get("min_healthy_hosts_threshold")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def response_time_threshold(self) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        '''(experimental) The Response Time threshold.

        :default: - No threshold.

        :stability: experimental
        '''
        result = self._values.get("response_time_threshold")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "TargetGroupMonitoringConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@condensetech/cdk-constructs.WidgetAlertAnnotationProps",
    jsii_struct_bases=[],
    name_mapping={"color": "color", "label": "label", "value": "value"},
)
class WidgetAlertAnnotationProps:
    def __init__(
        self,
        *,
        color: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        value: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param color: 
        :param label: 
        :param value: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__89455bf6261146031cb64d0d28df64ec214bc886d3f0b46b21c4af67b56515fa)
            check_type(argname="argument color", value=color, expected_type=type_hints["color"])
            check_type(argname="argument label", value=label, expected_type=type_hints["label"])
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if color is not None:
            self._values["color"] = color
        if label is not None:
            self._values["label"] = label
        if value is not None:
            self._values["value"] = value

    @builtins.property
    def color(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("color")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def label(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("label")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def value(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("value")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WidgetAlertAnnotationProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(IApplicationListenerPriorityAllocator)
class ApplicationListenerPriorityAllocator(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@condensetech/cdk-constructs.ApplicationListenerPriorityAllocator",
):
    '''(experimental) This custom resource allows to generate unique priorities for application listener rules.

    Consumers can allocate a priority to a listener rule by calling the ``allocatePriority`` method, ensuring that:

    - if no priority is set, one will be generated
    - if a priority is set, an error will be thrown if the priority is already taken

    :stability: experimental
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        listener: _aws_cdk_aws_elasticloadbalancingv2_ceddda9d.IApplicationListener,
        priority_allocator_name: typing.Optional[builtins.str] = None,
        priority_initial_value: typing.Optional[jsii.Number] = None,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param listener: (experimental) Application Load Balancer Listener to allocate priorities for.
        :param priority_allocator_name: (experimental) Priority Allocator name. Default: Generated by the listener unique name.
        :param priority_initial_value: (experimental) The initial priority value to start from. Default: 1
        :param removal_policy: (experimental) The removal policy to apply to the DynamoDB table. Default: - ``RemovalPolicy.DESTROY``

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f0b33f5852f61e5ad80aa8bc6b8b8a0774fe53a25aeaabb7e6d326db7c403611)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = ApplicationListenerPriorityAllocatorProps(
            listener=listener,
            priority_allocator_name=priority_allocator_name,
            priority_initial_value=priority_initial_value,
            removal_policy=removal_policy,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="fromPriorityAllocatorName")
    @builtins.classmethod
    def from_priority_allocator_name(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        priority_allocator_name: builtins.str,
    ) -> IApplicationListenerPriorityAllocator:
        '''
        :param scope: -
        :param id: -
        :param priority_allocator_name: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2cb22ab7d0fc51835785d6267c6699520e6284504956a924e3d48a825c1262a0)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument priority_allocator_name", value=priority_allocator_name, expected_type=type_hints["priority_allocator_name"])
        return typing.cast(IApplicationListenerPriorityAllocator, jsii.sinvoke(cls, "fromPriorityAllocatorName", [scope, id, priority_allocator_name]))

    @jsii.member(jsii_name="fromServiceToken")
    @builtins.classmethod
    def from_service_token(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        service_token: builtins.str,
    ) -> IApplicationListenerPriorityAllocator:
        '''
        :param scope: -
        :param id: -
        :param service_token: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ee5c94b5aeea053e8d5ce67f8781663bf3f44a9dde6c2719ff5b230c40b79c3d)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument service_token", value=service_token, expected_type=type_hints["service_token"])
        return typing.cast(IApplicationListenerPriorityAllocator, jsii.sinvoke(cls, "fromServiceToken", [scope, id, service_token]))

    @jsii.member(jsii_name="allocatePriority")
    def allocate_priority(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        priority: typing.Optional[jsii.Number] = None,
    ) -> jsii.Number:
        '''(experimental) Allocates the priority of an application listener rule.

        :param scope: The scope of the construct.
        :param id: The ID of the listener rule to allocate the priority to.
        :param priority: (experimental) The priority to allocate. Default: a priority will be allocated automatically.

        :return: The allocated priority.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e7d93e36d219bbbffd02e9ec5ef687591aab7747ad6ccacd73bebd3519fad280)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = AllocatePriorityProps(priority=priority)

        return typing.cast(jsii.Number, jsii.invoke(self, "allocatePriority", [scope, id, props]))

    @builtins.property
    @jsii.member(jsii_name="serviceToken")
    def service_token(self) -> builtins.str:
        '''(experimental) The service token to use to reference the custom resource.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "serviceToken"))


@jsii.implements(IDatabase)
class AuroraCluster(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@condensetech/cdk-constructs.AuroraCluster",
):
    '''(experimental) The AuroraCluster Construct creates an opinionated Aurora Cluster.

    Under the hood, it creates a `rds.DatabaseCluster <https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_rds-readme.html#starting-a-clustered-database>`_ construct.
    It implements the IDatabase interface so that it can be used in other constructs and stacks without requiring to access to the underlying construct.

    It also applies the following changes to the default behavior:

    - A `rds.ParameterGroup <https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_rds-readme.html#parameter-groups>`_ specific for the cluster is always defined.
      By using a custom parameter group instead of relying on the default one, a later change in the parameter group's parameters wouldn't require a replace of the cluster.
    - The credentials secret name is created after the construct's path. This way, the secret name is more readable and, when working with multiple stacks, can be easily inferred without having to rely on Cloudformation exports.
    - The default instance type for the writer instance is set to a minimum instance type based on the engine type.
    - The storage is always encrypted.
    - If the networking configuration includes a bastion host, the cluster allows connections from the bastion host.
    - The default security group name is ``${construct.node.path}-sg``. This allows for easier lookups when working with multiple stacks.

    :stability: experimental
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        engine: _aws_cdk_aws_rds_ceddda9d.IClusterEngine,
        networking: INetworking,
        backup_retention: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        cloudwatch_logs_exports: typing.Optional[typing.Sequence[builtins.str]] = None,
        cloudwatch_logs_retention: typing.Optional[_aws_cdk_aws_logs_ceddda9d.RetentionDays] = None,
        cluster_identifier: typing.Optional[builtins.str] = None,
        cluster_parameters: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        credentials_secret_name: typing.Optional[builtins.str] = None,
        credentials_username: typing.Optional[builtins.str] = None,
        database_name: typing.Optional[builtins.str] = None,
        instance_parameters: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        parameters: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        readers: typing.Optional[typing.Sequence[_aws_cdk_aws_rds_ceddda9d.IClusterInstance]] = None,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
        security_group_name: typing.Optional[builtins.str] = None,
        writer: typing.Optional[_aws_cdk_aws_rds_ceddda9d.IClusterInstance] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param engine: (experimental) The engine of the Aurora cluster.
        :param networking: (experimental) The networking configuration for the Aurora cluster.
        :param backup_retention: (experimental) The backup retention period. Default: - It uses the default applied by `rds.DatabaseClusterProps#backup <https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_rds.DatabaseClusterProps.html#backup>`_.
        :param cloudwatch_logs_exports: (experimental) The list of log types that need to be enabled for exporting to CloudWatch Logs. Default: - No log types are enabled.
        :param cloudwatch_logs_retention: (experimental) The number of days log events are kept in CloudWatch Logs. When updating this property, unsetting it doesn't remove the log retention policy. To remove the retention policy, set the value to Infinity. Default: logs never expire
        :param cluster_identifier: (experimental) The identifier of the cluster. If not specified, it relies on the underlying default naming.
        :param cluster_parameters: (experimental) The parameters to override in the cluster parameter group. Default: - No parameter is overridden.
        :param credentials_secret_name: (experimental) The name of the secret that stores the credentials of the database. Default: ``${construct.node.path}/secret``
        :param credentials_username: (experimental) The username of the database. Default: db_user
        :param database_name: (experimental) The name of the database. Default: - No default database is created.
        :param instance_parameters: (experimental) The parameters to override in the instance parameter group. Default: - No parameter is overridden.
        :param parameters: (experimental) The parameters to override in all of the parameter groups. Default: - No parameter is overridden.
        :param readers: (experimental) The reader instances of the Aurora cluster. Default: - No reader instances are created.
        :param removal_policy: (experimental) The removal policy to apply when the cluster is removed. Default: RemovalPolicy.RETAIN
        :param security_group_name: (experimental) The name of the security group. Default: - ``${construct.node.path}-sg``.
        :param writer: (experimental) The writer instance of the Aurora cluster. Default: - A provisioned instance with the minimum instance type based on the engine type.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__918e480e1b8c0172af87f81e840b4c6d9c58fba4979dc3a0c448041c4ee1d3b4)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = AuroraClusterProps(
            engine=engine,
            networking=networking,
            backup_retention=backup_retention,
            cloudwatch_logs_exports=cloudwatch_logs_exports,
            cloudwatch_logs_retention=cloudwatch_logs_retention,
            cluster_identifier=cluster_identifier,
            cluster_parameters=cluster_parameters,
            credentials_secret_name=credentials_secret_name,
            credentials_username=credentials_username,
            database_name=database_name,
            instance_parameters=instance_parameters,
            parameters=parameters,
            readers=readers,
            removal_policy=removal_policy,
            security_group_name=security_group_name,
            writer=writer,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="minimumInstanceType")
    @builtins.classmethod
    def minimum_instance_type(
        cls,
        engine: _aws_cdk_aws_rds_ceddda9d.IClusterEngine,
    ) -> _aws_cdk_aws_ec2_ceddda9d.InstanceType:
        '''(experimental) Returns the minimum instance type supported by the Aurora cluster based on the engine type.

        This method is used to set the default instance type for the writer instance if not otherwise specified.

        :param engine: The engine type of the Aurora cluster.

        :return: The minimum instance type supported by the Aurora cluster based on the engine type.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__675175b6caee5dfd5a620ef07239855087edc66870da74eb996e1d64a1c4a323)
            check_type(argname="argument engine", value=engine, expected_type=type_hints["engine"])
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.InstanceType, jsii.sinvoke(cls, "minimumInstanceType", [engine]))

    @jsii.member(jsii_name="fetchSecret")
    def fetch_secret(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: typing.Optional[builtins.str] = None,
    ) -> _aws_cdk_aws_secretsmanager_ceddda9d.ISecret:
        '''(experimental) Utility method that returns the secret with the credentials to access the database in a cross-stack compatible way.

        :param scope: -
        :param id: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5dffd8835158ac1142b018590ae1cc477906ec915c970cb7432434404f019e0f)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        return typing.cast(_aws_cdk_aws_secretsmanager_ceddda9d.ISecret, jsii.invoke(self, "fetchSecret", [scope, id]))

    @builtins.property
    @jsii.member(jsii_name="clusterParameterGroup")
    def cluster_parameter_group(self) -> _aws_cdk_aws_rds_ceddda9d.ParameterGroup:
        '''
        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_rds_ceddda9d.ParameterGroup, jsii.get(self, "clusterParameterGroup"))

    @builtins.property
    @jsii.member(jsii_name="connections")
    def connections(self) -> _aws_cdk_aws_ec2_ceddda9d.Connections:
        '''(experimental) The network connections associated with this resource.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.Connections, jsii.get(self, "connections"))

    @builtins.property
    @jsii.member(jsii_name="endpoint")
    def endpoint(self) -> _aws_cdk_aws_rds_ceddda9d.Endpoint:
        '''(experimental) The endpoint of the database.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_rds_ceddda9d.Endpoint, jsii.get(self, "endpoint"))

    @builtins.property
    @jsii.member(jsii_name="instanceParameterGroup")
    def instance_parameter_group(self) -> _aws_cdk_aws_rds_ceddda9d.ParameterGroup:
        '''
        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_rds_ceddda9d.ParameterGroup, jsii.get(self, "instanceParameterGroup"))

    @builtins.property
    @jsii.member(jsii_name="parameterGroup")
    def parameter_group(self) -> _aws_cdk_aws_rds_ceddda9d.ParameterGroup:
        '''
        :deprecated: please use instanceParameterGroup.

        :stability: deprecated
        '''
        return typing.cast(_aws_cdk_aws_rds_ceddda9d.ParameterGroup, jsii.get(self, "parameterGroup"))

    @builtins.property
    @jsii.member(jsii_name="resource")
    def resource(self) -> _aws_cdk_aws_rds_ceddda9d.DatabaseCluster:
        '''(experimental) The underlying database cluster.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_rds_ceddda9d.DatabaseCluster, jsii.get(self, "resource"))


@jsii.implements(IDatabase)
class AuroraClusterStack(
    _aws_cdk_ceddda9d.Stack,
    metaclass=jsii.JSIIMeta,
    jsii_type="@condensetech/cdk-constructs.AuroraClusterStack",
):
    '''(experimental) The AuroraClusterStack creates an `AuroraCluster <#@condensetech/cdk-constructs.AuroraCluster>`_ construct and optionally defines the monitoring configuration. It implements the IDatabase interface so that it can be used in other constructs and stacks without requiring to access to the underlying construct.

    :stability: experimental
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        monitoring: typing.Optional[typing.Union[MonitoringFacadeProps, typing.Dict[builtins.str, typing.Any]]] = None,
        engine: _aws_cdk_aws_rds_ceddda9d.IClusterEngine,
        networking: INetworking,
        backup_retention: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        cloudwatch_logs_exports: typing.Optional[typing.Sequence[builtins.str]] = None,
        cloudwatch_logs_retention: typing.Optional[_aws_cdk_aws_logs_ceddda9d.RetentionDays] = None,
        cluster_identifier: typing.Optional[builtins.str] = None,
        cluster_parameters: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        credentials_secret_name: typing.Optional[builtins.str] = None,
        credentials_username: typing.Optional[builtins.str] = None,
        database_name: typing.Optional[builtins.str] = None,
        instance_parameters: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        parameters: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        readers: typing.Optional[typing.Sequence[_aws_cdk_aws_rds_ceddda9d.IClusterInstance]] = None,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
        security_group_name: typing.Optional[builtins.str] = None,
        writer: typing.Optional[_aws_cdk_aws_rds_ceddda9d.IClusterInstance] = None,
        analytics_reporting: typing.Optional[builtins.bool] = None,
        cross_region_references: typing.Optional[builtins.bool] = None,
        description: typing.Optional[builtins.str] = None,
        env: typing.Optional[typing.Union[_aws_cdk_ceddda9d.Environment, typing.Dict[builtins.str, typing.Any]]] = None,
        permissions_boundary: typing.Optional[_aws_cdk_ceddda9d.PermissionsBoundary] = None,
        stack_name: typing.Optional[builtins.str] = None,
        suppress_template_indentation: typing.Optional[builtins.bool] = None,
        synthesizer: typing.Optional[_aws_cdk_ceddda9d.IStackSynthesizer] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        termination_protection: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param monitoring: (experimental) The monitoring configuration to apply to this stack. Default: - No monitoring.
        :param engine: (experimental) The engine of the Aurora cluster.
        :param networking: (experimental) The networking configuration for the Aurora cluster.
        :param backup_retention: (experimental) The backup retention period. Default: - It uses the default applied by `rds.DatabaseClusterProps#backup <https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_rds.DatabaseClusterProps.html#backup>`_.
        :param cloudwatch_logs_exports: (experimental) The list of log types that need to be enabled for exporting to CloudWatch Logs. Default: - No log types are enabled.
        :param cloudwatch_logs_retention: (experimental) The number of days log events are kept in CloudWatch Logs. When updating this property, unsetting it doesn't remove the log retention policy. To remove the retention policy, set the value to Infinity. Default: logs never expire
        :param cluster_identifier: (experimental) The identifier of the cluster. If not specified, it relies on the underlying default naming.
        :param cluster_parameters: (experimental) The parameters to override in the cluster parameter group. Default: - No parameter is overridden.
        :param credentials_secret_name: (experimental) The name of the secret that stores the credentials of the database. Default: ``${construct.node.path}/secret``
        :param credentials_username: (experimental) The username of the database. Default: db_user
        :param database_name: (experimental) The name of the database. Default: - No default database is created.
        :param instance_parameters: (experimental) The parameters to override in the instance parameter group. Default: - No parameter is overridden.
        :param parameters: (experimental) The parameters to override in all of the parameter groups. Default: - No parameter is overridden.
        :param readers: (experimental) The reader instances of the Aurora cluster. Default: - No reader instances are created.
        :param removal_policy: (experimental) The removal policy to apply when the cluster is removed. Default: RemovalPolicy.RETAIN
        :param security_group_name: (experimental) The name of the security group. Default: - ``${construct.node.path}-sg``.
        :param writer: (experimental) The writer instance of the Aurora cluster. Default: - A provisioned instance with the minimum instance type based on the engine type.
        :param analytics_reporting: Include runtime versioning information in this Stack. Default: ``analyticsReporting`` setting of containing ``App``, or value of 'aws:cdk:version-reporting' context key
        :param cross_region_references: Enable this flag to allow native cross region stack references. Enabling this will create a CloudFormation custom resource in both the producing stack and consuming stack in order to perform the export/import This feature is currently experimental Default: false
        :param description: A description of the stack. Default: - No description.
        :param env: The AWS environment (account/region) where this stack will be deployed. Set the ``region``/``account`` fields of ``env`` to either a concrete value to select the indicated environment (recommended for production stacks), or to the values of environment variables ``CDK_DEFAULT_REGION``/``CDK_DEFAULT_ACCOUNT`` to let the target environment depend on the AWS credentials/configuration that the CDK CLI is executed under (recommended for development stacks). If the ``Stack`` is instantiated inside a ``Stage``, any undefined ``region``/``account`` fields from ``env`` will default to the same field on the encompassing ``Stage``, if configured there. If either ``region`` or ``account`` are not set nor inherited from ``Stage``, the Stack will be considered "*environment-agnostic*"". Environment-agnostic stacks can be deployed to any environment but may not be able to take advantage of all features of the CDK. For example, they will not be able to use environmental context lookups such as ``ec2.Vpc.fromLookup`` and will not automatically translate Service Principals to the right format based on the environment's AWS partition, and other such enhancements. Default: - The environment of the containing ``Stage`` if available, otherwise create the stack will be environment-agnostic.
        :param permissions_boundary: Options for applying a permissions boundary to all IAM Roles and Users created within this Stage. Default: - no permissions boundary is applied
        :param stack_name: Name to deploy the stack with. Default: - Derived from construct path.
        :param suppress_template_indentation: Enable this flag to suppress indentation in generated CloudFormation templates. If not specified, the value of the ``@aws-cdk/core:suppressTemplateIndentation`` context key will be used. If that is not specified, then the default value ``false`` will be used. Default: - the value of ``@aws-cdk/core:suppressTemplateIndentation``, or ``false`` if that is not set.
        :param synthesizer: Synthesis method to use while deploying this stack. The Stack Synthesizer controls aspects of synthesis and deployment, like how assets are referenced and what IAM roles to use. For more information, see the README of the main CDK package. If not specified, the ``defaultStackSynthesizer`` from ``App`` will be used. If that is not specified, ``DefaultStackSynthesizer`` is used if ``@aws-cdk/core:newStyleStackSynthesis`` is set to ``true`` or the CDK major version is v2. In CDK v1 ``LegacyStackSynthesizer`` is the default if no other synthesizer is specified. Default: - The synthesizer specified on ``App``, or ``DefaultStackSynthesizer`` otherwise.
        :param tags: Stack tags that will be applied to all the taggable resources and the stack itself. Default: {}
        :param termination_protection: Whether to enable termination protection for this stack. Default: false

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cda33e503703b48b6026ca8d22c2708577a44c705b8a13324c75fa6c5337dd0a)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = AuroraClusterStackProps(
            monitoring=monitoring,
            engine=engine,
            networking=networking,
            backup_retention=backup_retention,
            cloudwatch_logs_exports=cloudwatch_logs_exports,
            cloudwatch_logs_retention=cloudwatch_logs_retention,
            cluster_identifier=cluster_identifier,
            cluster_parameters=cluster_parameters,
            credentials_secret_name=credentials_secret_name,
            credentials_username=credentials_username,
            database_name=database_name,
            instance_parameters=instance_parameters,
            parameters=parameters,
            readers=readers,
            removal_policy=removal_policy,
            security_group_name=security_group_name,
            writer=writer,
            analytics_reporting=analytics_reporting,
            cross_region_references=cross_region_references,
            description=description,
            env=env,
            permissions_boundary=permissions_boundary,
            stack_name=stack_name,
            suppress_template_indentation=suppress_template_indentation,
            synthesizer=synthesizer,
            tags=tags,
            termination_protection=termination_protection,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="fetchSecret")
    def fetch_secret(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: typing.Optional[builtins.str] = None,
    ) -> _aws_cdk_aws_secretsmanager_ceddda9d.ISecret:
        '''(experimental) Utility method that returns the secret with the credentials to access the database in a cross-stack compatible way.

        :param scope: -
        :param id: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8992950dcef6a8a7769c27b826324c48b64ebe4c26e220e72fa33671b315ee04)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        return typing.cast(_aws_cdk_aws_secretsmanager_ceddda9d.ISecret, jsii.invoke(self, "fetchSecret", [scope, id]))

    @builtins.property
    @jsii.member(jsii_name="connections")
    def connections(self) -> _aws_cdk_aws_ec2_ceddda9d.Connections:
        '''(experimental) The network connections associated with this resource.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.Connections, jsii.get(self, "connections"))

    @builtins.property
    @jsii.member(jsii_name="endpoint")
    def endpoint(self) -> _aws_cdk_aws_rds_ceddda9d.Endpoint:
        '''(experimental) The endpoint of the database.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_rds_ceddda9d.Endpoint, jsii.get(self, "endpoint"))

    @builtins.property
    @jsii.member(jsii_name="resource")
    def resource(self) -> AuroraCluster:
        '''(experimental) Underlying AuroraCluster construct.

        :stability: experimental
        '''
        return typing.cast(AuroraCluster, jsii.get(self, "resource"))


@jsii.implements(IDatabase)
class DatabaseInstance(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@condensetech/cdk-constructs.DatabaseInstance",
):
    '''(experimental) The DatabaseInstance construct creates an RDS database instance.

    Under the hood, it creates a `rds.DatabaseInstance <https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_rds-readme.html#starting-an-instance-database>`_ construct.
    It implements the IDatabase interface so that it can be used in other constructs and stacks without requiring to access to the underlying construct.

    It also applies the following changes to the default behavior:

    - A `rds.ParameterGroup <https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_rds-readme.html#parameter-groups>`_ specific for the cluster is always defined.
      By using a custom parameter group instead of relying on the default one, a later change in the parameter group's parameters wouldn't require a replace of the cluster.
    - The credentials secret name is created after the construct's path. This way, the secret name is more readable and, when working with multiple stacks, can be easily inferred without having to rely on Cloudformation exports.
    - It defaults the storage type to GP3 when not specified.
    - It defaults the allocated storage to the minimum storage of 20 GB when not specified.
    - The default instance type is set to t3.small.
    - The storage is always encrypted.
    - If the networking configuration includes a bastion host, the database allows connections from the bastion host.
    - The default security group name is ``${construct.node.path}-sg``. This allows for easier lookups when working with multiple stacks.

    :stability: experimental
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        engine: _aws_cdk_aws_rds_ceddda9d.IInstanceEngine,
        networking: INetworking,
        allocated_storage: typing.Optional[jsii.Number] = None,
        allow_major_version_upgrade: typing.Optional[builtins.bool] = None,
        backup_retention: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        cloudwatch_logs_exports: typing.Optional[typing.Sequence[builtins.str]] = None,
        cloudwatch_logs_retention: typing.Optional[_aws_cdk_aws_logs_ceddda9d.RetentionDays] = None,
        credentials_secret_name: typing.Optional[builtins.str] = None,
        credentials_username: typing.Optional[builtins.str] = None,
        database_name: typing.Optional[builtins.str] = None,
        enable_performance_insights: typing.Optional[builtins.bool] = None,
        instance_identifier: typing.Optional[builtins.str] = None,
        instance_type: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.InstanceType] = None,
        max_allocated_storage: typing.Optional[jsii.Number] = None,
        multi_az: typing.Optional[builtins.bool] = None,
        parameters: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
        security_group_name: typing.Optional[builtins.str] = None,
        storage_type: typing.Optional[_aws_cdk_aws_rds_ceddda9d.StorageType] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param engine: (experimental) The engine of the database instance.
        :param networking: (experimental) The networking configuration for the database instance.
        :param allocated_storage: (experimental) The allocated storage of the database instance. Default: 20
        :param allow_major_version_upgrade: (experimental) Whether to allow major version upgrades. Default: false
        :param backup_retention: (experimental) The backup retention period. Default: - It uses the default applied by [rds.DatabaseInstanceProps#backupRetention]https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_rds.DatabaseInstanceProps.html#backupretention).
        :param cloudwatch_logs_exports: (experimental) The list of log types that need to be enabled for exporting to CloudWatch Logs. Default: - No log types are enabled.
        :param cloudwatch_logs_retention: (experimental) The number of days log events are kept in CloudWatch Logs. When updating this property, unsetting it doesn't remove the log retention policy. To remove the retention policy, set the value to Infinity. Default: logs never expire
        :param credentials_secret_name: (experimental) The name of the secret that stores the credentials of the database. Default: ``${construct.node.path}/secret``
        :param credentials_username: (experimental) The username of the database. Default: db_user
        :param database_name: (experimental) The name of the database. Default: - No default database is created.
        :param enable_performance_insights: (experimental) Whether to enable Performance Insights. Default: false
        :param instance_identifier: (experimental) The identifier of the database instance. Default: - No identifier is specified.
        :param instance_type: (experimental) The instance type of the database instance. Default: - db.t3.small.
        :param max_allocated_storage: (experimental) The maximum allocated storage of the database instance. Default: - No maximum allocated storage is specified.
        :param multi_az: (experimental) If the database instance is multi-AZ. Default: false
        :param parameters: (experimental) The parameters to override in the parameter group. Default: - No parameter is overridden.
        :param removal_policy: (experimental) The removal policy to apply when the cluster is removed. Default: RemovalPolicy.RETAIN
        :param security_group_name: (experimental) The name of the security group. Default: - ``${construct.node.path}-sg``.
        :param storage_type: (experimental) The storage type of the database instance. Default: rds.StorageType.GP3

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0140b7dc73cbbd21efe34e542cab574c9dd014c3f5aa2cdd846b759a05a95a0e)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = DatabaseInstanceProps(
            engine=engine,
            networking=networking,
            allocated_storage=allocated_storage,
            allow_major_version_upgrade=allow_major_version_upgrade,
            backup_retention=backup_retention,
            cloudwatch_logs_exports=cloudwatch_logs_exports,
            cloudwatch_logs_retention=cloudwatch_logs_retention,
            credentials_secret_name=credentials_secret_name,
            credentials_username=credentials_username,
            database_name=database_name,
            enable_performance_insights=enable_performance_insights,
            instance_identifier=instance_identifier,
            instance_type=instance_type,
            max_allocated_storage=max_allocated_storage,
            multi_az=multi_az,
            parameters=parameters,
            removal_policy=removal_policy,
            security_group_name=security_group_name,
            storage_type=storage_type,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="fetchSecret")
    def fetch_secret(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: typing.Optional[builtins.str] = None,
    ) -> _aws_cdk_aws_secretsmanager_ceddda9d.ISecret:
        '''(experimental) Utility method that returns the secret with the credentials to access the database in a cross-stack compatible way.

        :param scope: -
        :param id: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b66785938111d23423861844f79752b5d1db28e61ea7a8bd09083c65704b9826)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        return typing.cast(_aws_cdk_aws_secretsmanager_ceddda9d.ISecret, jsii.invoke(self, "fetchSecret", [scope, id]))

    @builtins.property
    @jsii.member(jsii_name="connections")
    def connections(self) -> _aws_cdk_aws_ec2_ceddda9d.Connections:
        '''(experimental) The network connections associated with this resource.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.Connections, jsii.get(self, "connections"))

    @builtins.property
    @jsii.member(jsii_name="endpoint")
    def endpoint(self) -> _aws_cdk_aws_rds_ceddda9d.Endpoint:
        '''(experimental) The endpoint of the database.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_rds_ceddda9d.Endpoint, jsii.get(self, "endpoint"))

    @builtins.property
    @jsii.member(jsii_name="resource")
    def resource(self) -> _aws_cdk_aws_rds_ceddda9d.IDatabaseInstance:
        '''(experimental) The underlying RDS database instance.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_rds_ceddda9d.IDatabaseInstance, jsii.get(self, "resource"))


@jsii.implements(IDatabase)
class DatabaseInstanceStack(
    _aws_cdk_ceddda9d.Stack,
    metaclass=jsii.JSIIMeta,
    jsii_type="@condensetech/cdk-constructs.DatabaseInstanceStack",
):
    '''(experimental) The DatabaseInstanceStack creates a `DatabaseInstance <#@condensetech/cdk-constructs.DatabaseInstance>`_ construct and optionally defines the monitoring configuration. It implements the IDatabase interface so that it can be used in other constructs and stacks without requiring to access to the underlying construct.

    :stability: experimental
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        monitoring: typing.Optional[typing.Union[MonitoringFacadeProps, typing.Dict[builtins.str, typing.Any]]] = None,
        engine: _aws_cdk_aws_rds_ceddda9d.IInstanceEngine,
        networking: INetworking,
        allocated_storage: typing.Optional[jsii.Number] = None,
        allow_major_version_upgrade: typing.Optional[builtins.bool] = None,
        backup_retention: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        cloudwatch_logs_exports: typing.Optional[typing.Sequence[builtins.str]] = None,
        cloudwatch_logs_retention: typing.Optional[_aws_cdk_aws_logs_ceddda9d.RetentionDays] = None,
        credentials_secret_name: typing.Optional[builtins.str] = None,
        credentials_username: typing.Optional[builtins.str] = None,
        database_name: typing.Optional[builtins.str] = None,
        enable_performance_insights: typing.Optional[builtins.bool] = None,
        instance_identifier: typing.Optional[builtins.str] = None,
        instance_type: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.InstanceType] = None,
        max_allocated_storage: typing.Optional[jsii.Number] = None,
        multi_az: typing.Optional[builtins.bool] = None,
        parameters: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
        security_group_name: typing.Optional[builtins.str] = None,
        storage_type: typing.Optional[_aws_cdk_aws_rds_ceddda9d.StorageType] = None,
        analytics_reporting: typing.Optional[builtins.bool] = None,
        cross_region_references: typing.Optional[builtins.bool] = None,
        description: typing.Optional[builtins.str] = None,
        env: typing.Optional[typing.Union[_aws_cdk_ceddda9d.Environment, typing.Dict[builtins.str, typing.Any]]] = None,
        permissions_boundary: typing.Optional[_aws_cdk_ceddda9d.PermissionsBoundary] = None,
        stack_name: typing.Optional[builtins.str] = None,
        suppress_template_indentation: typing.Optional[builtins.bool] = None,
        synthesizer: typing.Optional[_aws_cdk_ceddda9d.IStackSynthesizer] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        termination_protection: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param monitoring: (experimental) The monitoring configuration to apply to this stack. Default: - No monitoring.
        :param engine: (experimental) The engine of the database instance.
        :param networking: (experimental) The networking configuration for the database instance.
        :param allocated_storage: (experimental) The allocated storage of the database instance. Default: 20
        :param allow_major_version_upgrade: (experimental) Whether to allow major version upgrades. Default: false
        :param backup_retention: (experimental) The backup retention period. Default: - It uses the default applied by [rds.DatabaseInstanceProps#backupRetention]https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_rds.DatabaseInstanceProps.html#backupretention).
        :param cloudwatch_logs_exports: (experimental) The list of log types that need to be enabled for exporting to CloudWatch Logs. Default: - No log types are enabled.
        :param cloudwatch_logs_retention: (experimental) The number of days log events are kept in CloudWatch Logs. When updating this property, unsetting it doesn't remove the log retention policy. To remove the retention policy, set the value to Infinity. Default: logs never expire
        :param credentials_secret_name: (experimental) The name of the secret that stores the credentials of the database. Default: ``${construct.node.path}/secret``
        :param credentials_username: (experimental) The username of the database. Default: db_user
        :param database_name: (experimental) The name of the database. Default: - No default database is created.
        :param enable_performance_insights: (experimental) Whether to enable Performance Insights. Default: false
        :param instance_identifier: (experimental) The identifier of the database instance. Default: - No identifier is specified.
        :param instance_type: (experimental) The instance type of the database instance. Default: - db.t3.small.
        :param max_allocated_storage: (experimental) The maximum allocated storage of the database instance. Default: - No maximum allocated storage is specified.
        :param multi_az: (experimental) If the database instance is multi-AZ. Default: false
        :param parameters: (experimental) The parameters to override in the parameter group. Default: - No parameter is overridden.
        :param removal_policy: (experimental) The removal policy to apply when the cluster is removed. Default: RemovalPolicy.RETAIN
        :param security_group_name: (experimental) The name of the security group. Default: - ``${construct.node.path}-sg``.
        :param storage_type: (experimental) The storage type of the database instance. Default: rds.StorageType.GP3
        :param analytics_reporting: Include runtime versioning information in this Stack. Default: ``analyticsReporting`` setting of containing ``App``, or value of 'aws:cdk:version-reporting' context key
        :param cross_region_references: Enable this flag to allow native cross region stack references. Enabling this will create a CloudFormation custom resource in both the producing stack and consuming stack in order to perform the export/import This feature is currently experimental Default: false
        :param description: A description of the stack. Default: - No description.
        :param env: The AWS environment (account/region) where this stack will be deployed. Set the ``region``/``account`` fields of ``env`` to either a concrete value to select the indicated environment (recommended for production stacks), or to the values of environment variables ``CDK_DEFAULT_REGION``/``CDK_DEFAULT_ACCOUNT`` to let the target environment depend on the AWS credentials/configuration that the CDK CLI is executed under (recommended for development stacks). If the ``Stack`` is instantiated inside a ``Stage``, any undefined ``region``/``account`` fields from ``env`` will default to the same field on the encompassing ``Stage``, if configured there. If either ``region`` or ``account`` are not set nor inherited from ``Stage``, the Stack will be considered "*environment-agnostic*"". Environment-agnostic stacks can be deployed to any environment but may not be able to take advantage of all features of the CDK. For example, they will not be able to use environmental context lookups such as ``ec2.Vpc.fromLookup`` and will not automatically translate Service Principals to the right format based on the environment's AWS partition, and other such enhancements. Default: - The environment of the containing ``Stage`` if available, otherwise create the stack will be environment-agnostic.
        :param permissions_boundary: Options for applying a permissions boundary to all IAM Roles and Users created within this Stage. Default: - no permissions boundary is applied
        :param stack_name: Name to deploy the stack with. Default: - Derived from construct path.
        :param suppress_template_indentation: Enable this flag to suppress indentation in generated CloudFormation templates. If not specified, the value of the ``@aws-cdk/core:suppressTemplateIndentation`` context key will be used. If that is not specified, then the default value ``false`` will be used. Default: - the value of ``@aws-cdk/core:suppressTemplateIndentation``, or ``false`` if that is not set.
        :param synthesizer: Synthesis method to use while deploying this stack. The Stack Synthesizer controls aspects of synthesis and deployment, like how assets are referenced and what IAM roles to use. For more information, see the README of the main CDK package. If not specified, the ``defaultStackSynthesizer`` from ``App`` will be used. If that is not specified, ``DefaultStackSynthesizer`` is used if ``@aws-cdk/core:newStyleStackSynthesis`` is set to ``true`` or the CDK major version is v2. In CDK v1 ``LegacyStackSynthesizer`` is the default if no other synthesizer is specified. Default: - The synthesizer specified on ``App``, or ``DefaultStackSynthesizer`` otherwise.
        :param tags: Stack tags that will be applied to all the taggable resources and the stack itself. Default: {}
        :param termination_protection: Whether to enable termination protection for this stack. Default: false

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0a3c3637d08962f782b0f4015419c22e4d8fd0d21f593f42460e5ceb6df442e2)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = DatabaseInstanceStackProps(
            monitoring=monitoring,
            engine=engine,
            networking=networking,
            allocated_storage=allocated_storage,
            allow_major_version_upgrade=allow_major_version_upgrade,
            backup_retention=backup_retention,
            cloudwatch_logs_exports=cloudwatch_logs_exports,
            cloudwatch_logs_retention=cloudwatch_logs_retention,
            credentials_secret_name=credentials_secret_name,
            credentials_username=credentials_username,
            database_name=database_name,
            enable_performance_insights=enable_performance_insights,
            instance_identifier=instance_identifier,
            instance_type=instance_type,
            max_allocated_storage=max_allocated_storage,
            multi_az=multi_az,
            parameters=parameters,
            removal_policy=removal_policy,
            security_group_name=security_group_name,
            storage_type=storage_type,
            analytics_reporting=analytics_reporting,
            cross_region_references=cross_region_references,
            description=description,
            env=env,
            permissions_boundary=permissions_boundary,
            stack_name=stack_name,
            suppress_template_indentation=suppress_template_indentation,
            synthesizer=synthesizer,
            tags=tags,
            termination_protection=termination_protection,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="fetchSecret")
    def fetch_secret(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: typing.Optional[builtins.str] = None,
    ) -> _aws_cdk_aws_secretsmanager_ceddda9d.ISecret:
        '''(experimental) Utility method that returns the secret with the credentials to access the database in a cross-stack compatible way.

        :param scope: -
        :param id: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__23f0915d15304e34335fbfdb975e4739d91e3b735de6d3222d3eb061eb7e6340)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        return typing.cast(_aws_cdk_aws_secretsmanager_ceddda9d.ISecret, jsii.invoke(self, "fetchSecret", [scope, id]))

    @builtins.property
    @jsii.member(jsii_name="connections")
    def connections(self) -> _aws_cdk_aws_ec2_ceddda9d.Connections:
        '''(experimental) The network connections associated with this resource.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.Connections, jsii.get(self, "connections"))

    @builtins.property
    @jsii.member(jsii_name="endpoint")
    def endpoint(self) -> _aws_cdk_aws_rds_ceddda9d.Endpoint:
        '''(experimental) The endpoint of the database.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_rds_ceddda9d.Endpoint, jsii.get(self, "endpoint"))

    @builtins.property
    @jsii.member(jsii_name="resource")
    def resource(self) -> DatabaseInstance:
        '''(experimental) Underlying DatabaseInstance construct.

        :stability: experimental
        '''
        return typing.cast(DatabaseInstance, jsii.get(self, "resource"))


@jsii.implements(IEntrypoint)
class Entrypoint(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@condensetech/cdk-constructs.Entrypoint",
):
    '''(experimental) The Entrypoint construct creates an Application Load Balancer (ALB) that serves as the centralized entry point for all applications.

    This ALB is shared across multiple applications, primarily to optimize infrastructure costs by reducing the need for multiple load balancers.
    It implements the IEntrypoint interface so that it can be used in other constructs and stacks without requiring to access to the underlying construct.

    It creates an ALB with:

    - an HTTP listener that redirects all traffic to HTTPS.
    - an HTTPS listener that returns a 403 Forbidden response by default.
    - a custom security group. This allows to expose the security group as a property of the entrypoint construct, making it easier to reference it in other constructs.
      Finally, it creates the Route 53 A and AAAA record that point to the ALB.

    When hostedZoneProps is provided, by default this construct creates an HTTPS certificate, bound to the domain name and all subdomains (unless wildcardCertificate is set to false).
    You can also provide an existing certificate ARN through certificate.certificateArn.

    When an ``entrypointName`` is provided, this is used as the name of the ALB and as the prefix for the security group.
    It is also used to add an additional "Name" tag to the load balancer.
    This helps to use `ApplicationLoadBalancer#lookup <https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_elasticloadbalancingv2.ApplicationLoadBalancer.html#static-fromwbrlookupscope-id-options>`_ to find the load balancer by name.

    :stability: experimental
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        domain_name: builtins.str,
        networking: INetworking,
        certificate: typing.Optional[typing.Union[EntrypointCertificateProps, typing.Dict[builtins.str, typing.Any]]] = None,
        certificates: typing.Optional[typing.Sequence[typing.Union[EntrypointCertificateProps, typing.Dict[builtins.str, typing.Any]]]] = None,
        entrypoint_name: typing.Optional[builtins.str] = None,
        entrypoint_security_group_name: typing.Optional[builtins.str] = None,
        hosted_zone_props: typing.Optional[typing.Union[_aws_cdk_aws_route53_ceddda9d.HostedZoneAttributes, typing.Dict[builtins.str, typing.Any]]] = None,
        logs_bucket: typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket] = None,
        priority_allocator: typing.Optional[typing.Union[ApplicationListenerPriorityAllocatorConfig, typing.Dict[builtins.str, typing.Any]]] = None,
        security_group_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param domain_name: (experimental) The domain name to which the entrypoint is associated.
        :param networking: (experimental) The networking configuration for the entrypoint.
        :param certificate: (deprecated) Certificate properties for the entrypoint. Default: - A new certificate is created through ACM, bound to domainName, *.domainName.
        :param certificates: (experimental) Certificate properties for the entrypoint. Default: - A new certificate is created through ACM, bound to domainName, *.domainName.
        :param entrypoint_name: (experimental) The name of the entrypoint. This value is used as the name of the underlying Application Load Balancer (ALB) and as the prefix for the name of the associated security group. Default: - No name is specified.
        :param entrypoint_security_group_name: (deprecated) The name of the security group for the entrypoint. Default: ``${entrypointName}-sg``
        :param hosted_zone_props: (experimental) The Route 53 hosted zone attributes for the domain name.
        :param logs_bucket: (experimental) The S3 bucket to store the logs of the ALB. Setting this will enable the access logs for the ALB. Default: - Logging is disabled.
        :param priority_allocator: (experimental) Customize the priority allocator for the entrypoint.
        :param security_group_name: (experimental) The name of the security group for the entrypoint. Default: ``${entrypointName}-sg`` if ``entrypointName`` is specified, otherwise no name is specified.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__43117885de9d29986a3fba3fd54947e369ad7fcb99dfbb6e11b21e69a743eb0f)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = EntrypointProps(
            domain_name=domain_name,
            networking=networking,
            certificate=certificate,
            certificates=certificates,
            entrypoint_name=entrypoint_name,
            entrypoint_security_group_name=entrypoint_security_group_name,
            hosted_zone_props=hosted_zone_props,
            logs_bucket=logs_bucket,
            priority_allocator=priority_allocator,
            security_group_name=security_group_name,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="fromAttributes")
    @builtins.classmethod
    def from_attributes(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        listener_arn: builtins.str,
        load_balancer_arn: builtins.str,
        security_group_id: builtins.str,
        domain_name: typing.Optional[builtins.str] = None,
        entrypoint_name: typing.Optional[builtins.str] = None,
        priority_allocator_service_token: typing.Optional[builtins.str] = None,
    ) -> IEntrypoint:
        '''
        :param scope: -
        :param id: -
        :param listener_arn: (experimental) ARN of the load balancer HTTPS listener.
        :param load_balancer_arn: (experimental) The load balancer ARN.
        :param security_group_id: (experimental) The security group ID of the load balancer.
        :param domain_name: (experimental) The load balancer custom domain name. Default: - No domain name is specified, and the load balancer dns name will be used.
        :param entrypoint_name: (experimental) The entrypoint name to use for referencing the priority allocator.
        :param priority_allocator_service_token: (experimental) The Priority Allocator service token to use for referencing the priority allocator.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b43eb05048147e42be7ce96ae5872d2446ab14c342edc5bf6f712875dd6483e2)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = EntrypointFromAttributes(
            listener_arn=listener_arn,
            load_balancer_arn=load_balancer_arn,
            security_group_id=security_group_id,
            domain_name=domain_name,
            entrypoint_name=entrypoint_name,
            priority_allocator_service_token=priority_allocator_service_token,
        )

        return typing.cast(IEntrypoint, jsii.sinvoke(cls, "fromAttributes", [scope, id, props]))

    @jsii.member(jsii_name="fromLookup")
    @builtins.classmethod
    def from_lookup(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        entrypoint_name: builtins.str,
        domain_name: typing.Optional[builtins.str] = None,
        vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
        vpc_lookup: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.VpcLookupOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> IEntrypoint:
        '''
        :param scope: -
        :param id: -
        :param entrypoint_name: (experimental) The entrypoint name to lookup.
        :param domain_name: (experimental) The load balancer custom domain name. Default: - No domain name is specified, and the load balancer dns name will be used.
        :param vpc: (experimental) The VPC where the entrypoint is located. Required if vpcLookup is not provided.
        :param vpc_lookup: (experimental) The VPC lookup options to find the VPC where the entrypoint is located. Required if vpc is not provided.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c307e05e08316e6716948431c89526e1e1f7f44d5d4eab8fc84fb48adcbf29ab)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = EntrypointFromLookupProps(
            entrypoint_name=entrypoint_name,
            domain_name=domain_name,
            vpc=vpc,
            vpc_lookup=vpc_lookup,
        )

        return typing.cast(IEntrypoint, jsii.sinvoke(cls, "fromLookup", [scope, id, props]))

    @jsii.member(jsii_name="allocateListenerRule")
    def allocate_listener_rule(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        action: typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ListenerAction] = None,
        conditions: typing.Optional[typing.Sequence[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ListenerCondition]] = None,
        priority: typing.Optional[jsii.Number] = None,
        target_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.IApplicationTargetGroup]] = None,
    ) -> _aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ApplicationListenerRule:
        '''(experimental) It creates an ApplicationListenerRule for the HTTPS listener of the Entrypoint.

        This method doesn't require a priority to be explicitly set, and tracks the allocated priorities on a DynamoDB table to avoid conflicts.

        :param scope: -
        :param id: -
        :param action: (experimental) Action to perform when requests are received. Only one of ``action``, ``fixedResponse``, ``redirectResponse`` or ``targetGroups`` can be specified. Default: - No action
        :param conditions: (experimental) Rule applies if matches the conditions. Default: - No conditions.
        :param priority: (experimental) Priority of the rule. The rule with the lowest priority will be used for every request. Default: - The rule will be assigned a priority automatically.
        :param target_groups: (experimental) Target groups to forward requests to. Only one of ``action``, ``fixedResponse``, ``redirectResponse`` or ``targetGroups`` can be specified. Implies a ``forward`` action. Default: - No target groups.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__445a7303c95b2fbb5bb62936f599717a2ce079e4765066c8938348b92a8c9d92)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = AllocateApplicationListenerRuleProps(
            action=action,
            conditions=conditions,
            priority=priority,
            target_groups=target_groups,
        )

        return typing.cast(_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ApplicationListenerRule, jsii.invoke(self, "allocateListenerRule", [scope, id, props]))

    @jsii.member(jsii_name="referenceListener")
    def reference_listener(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
    ) -> _aws_cdk_aws_elasticloadbalancingv2_ceddda9d.IApplicationListener:
        '''(experimental) Utility method that returns the HTTPS listener of the entrypoint in a cross-stack compatible way.

        :param scope: -
        :param id: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c3fa4b14f324947bf3a512c16e6bae2a98a5d57e38faa72de2acedbcb6f1b8a3)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        return typing.cast(_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.IApplicationListener, jsii.invoke(self, "referenceListener", [scope, id]))

    @builtins.property
    @jsii.member(jsii_name="alb")
    def alb(
        self,
    ) -> _aws_cdk_aws_elasticloadbalancingv2_ceddda9d.IApplicationLoadBalancer:
        '''(experimental) The ALB that serves as the entrypoint.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.IApplicationLoadBalancer, jsii.get(self, "alb"))

    @builtins.property
    @jsii.member(jsii_name="domainName")
    def domain_name(self) -> builtins.str:
        '''(experimental) The load balancer custom domain name.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "domainName"))

    @builtins.property
    @jsii.member(jsii_name="listener")
    def listener(
        self,
    ) -> _aws_cdk_aws_elasticloadbalancingv2_ceddda9d.IApplicationListener:
        '''
        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.IApplicationListener, jsii.get(self, "listener"))

    @builtins.property
    @jsii.member(jsii_name="priorityAllocator")
    def priority_allocator(self) -> IApplicationListenerPriorityAllocator:
        '''(experimental) The Application Listener priority allocator for the entrypoint.

        :stability: experimental
        '''
        return typing.cast(IApplicationListenerPriorityAllocator, jsii.get(self, "priorityAllocator"))

    @builtins.property
    @jsii.member(jsii_name="securityGroup")
    def security_group(self) -> _aws_cdk_aws_ec2_ceddda9d.ISecurityGroup:
        '''
        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup, jsii.get(self, "securityGroup"))


@jsii.implements(IEntrypoint)
class EntrypointStack(
    _aws_cdk_ceddda9d.Stack,
    metaclass=jsii.JSIIMeta,
    jsii_type="@condensetech/cdk-constructs.EntrypointStack",
):
    '''(experimental) The EntrypointStack creates an `Entrypoint <#@condensetech/cdk-constructs.Entrypoint>`_ construct and optionally defines the monitoring configuration. It implements the IEntrypoint interface so that it can be used in other constructs and stacks without requiring to access to the underlying construct.

    :stability: experimental
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        monitoring: typing.Optional[typing.Union[MonitoringFacadeProps, typing.Dict[builtins.str, typing.Any]]] = None,
        domain_name: builtins.str,
        networking: INetworking,
        certificate: typing.Optional[typing.Union[EntrypointCertificateProps, typing.Dict[builtins.str, typing.Any]]] = None,
        certificates: typing.Optional[typing.Sequence[typing.Union[EntrypointCertificateProps, typing.Dict[builtins.str, typing.Any]]]] = None,
        entrypoint_name: typing.Optional[builtins.str] = None,
        entrypoint_security_group_name: typing.Optional[builtins.str] = None,
        hosted_zone_props: typing.Optional[typing.Union[_aws_cdk_aws_route53_ceddda9d.HostedZoneAttributes, typing.Dict[builtins.str, typing.Any]]] = None,
        logs_bucket: typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket] = None,
        priority_allocator: typing.Optional[typing.Union[ApplicationListenerPriorityAllocatorConfig, typing.Dict[builtins.str, typing.Any]]] = None,
        security_group_name: typing.Optional[builtins.str] = None,
        analytics_reporting: typing.Optional[builtins.bool] = None,
        cross_region_references: typing.Optional[builtins.bool] = None,
        description: typing.Optional[builtins.str] = None,
        env: typing.Optional[typing.Union[_aws_cdk_ceddda9d.Environment, typing.Dict[builtins.str, typing.Any]]] = None,
        permissions_boundary: typing.Optional[_aws_cdk_ceddda9d.PermissionsBoundary] = None,
        stack_name: typing.Optional[builtins.str] = None,
        suppress_template_indentation: typing.Optional[builtins.bool] = None,
        synthesizer: typing.Optional[_aws_cdk_ceddda9d.IStackSynthesizer] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        termination_protection: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param monitoring: (experimental) The monitoring configuration to apply to this stack. Default: - No monitoring.
        :param domain_name: (experimental) The domain name to which the entrypoint is associated.
        :param networking: (experimental) The networking configuration for the entrypoint.
        :param certificate: (deprecated) Certificate properties for the entrypoint. Default: - A new certificate is created through ACM, bound to domainName, *.domainName.
        :param certificates: (experimental) Certificate properties for the entrypoint. Default: - A new certificate is created through ACM, bound to domainName, *.domainName.
        :param entrypoint_name: (experimental) The name of the entrypoint. This value is used as the name of the underlying Application Load Balancer (ALB) and as the prefix for the name of the associated security group. Default: - No name is specified.
        :param entrypoint_security_group_name: (deprecated) The name of the security group for the entrypoint. Default: ``${entrypointName}-sg``
        :param hosted_zone_props: (experimental) The Route 53 hosted zone attributes for the domain name.
        :param logs_bucket: (experimental) The S3 bucket to store the logs of the ALB. Setting this will enable the access logs for the ALB. Default: - Logging is disabled.
        :param priority_allocator: (experimental) Customize the priority allocator for the entrypoint.
        :param security_group_name: (experimental) The name of the security group for the entrypoint. Default: ``${entrypointName}-sg`` if ``entrypointName`` is specified, otherwise no name is specified.
        :param analytics_reporting: Include runtime versioning information in this Stack. Default: ``analyticsReporting`` setting of containing ``App``, or value of 'aws:cdk:version-reporting' context key
        :param cross_region_references: Enable this flag to allow native cross region stack references. Enabling this will create a CloudFormation custom resource in both the producing stack and consuming stack in order to perform the export/import This feature is currently experimental Default: false
        :param description: A description of the stack. Default: - No description.
        :param env: The AWS environment (account/region) where this stack will be deployed. Set the ``region``/``account`` fields of ``env`` to either a concrete value to select the indicated environment (recommended for production stacks), or to the values of environment variables ``CDK_DEFAULT_REGION``/``CDK_DEFAULT_ACCOUNT`` to let the target environment depend on the AWS credentials/configuration that the CDK CLI is executed under (recommended for development stacks). If the ``Stack`` is instantiated inside a ``Stage``, any undefined ``region``/``account`` fields from ``env`` will default to the same field on the encompassing ``Stage``, if configured there. If either ``region`` or ``account`` are not set nor inherited from ``Stage``, the Stack will be considered "*environment-agnostic*"". Environment-agnostic stacks can be deployed to any environment but may not be able to take advantage of all features of the CDK. For example, they will not be able to use environmental context lookups such as ``ec2.Vpc.fromLookup`` and will not automatically translate Service Principals to the right format based on the environment's AWS partition, and other such enhancements. Default: - The environment of the containing ``Stage`` if available, otherwise create the stack will be environment-agnostic.
        :param permissions_boundary: Options for applying a permissions boundary to all IAM Roles and Users created within this Stage. Default: - no permissions boundary is applied
        :param stack_name: Name to deploy the stack with. Default: - Derived from construct path.
        :param suppress_template_indentation: Enable this flag to suppress indentation in generated CloudFormation templates. If not specified, the value of the ``@aws-cdk/core:suppressTemplateIndentation`` context key will be used. If that is not specified, then the default value ``false`` will be used. Default: - the value of ``@aws-cdk/core:suppressTemplateIndentation``, or ``false`` if that is not set.
        :param synthesizer: Synthesis method to use while deploying this stack. The Stack Synthesizer controls aspects of synthesis and deployment, like how assets are referenced and what IAM roles to use. For more information, see the README of the main CDK package. If not specified, the ``defaultStackSynthesizer`` from ``App`` will be used. If that is not specified, ``DefaultStackSynthesizer`` is used if ``@aws-cdk/core:newStyleStackSynthesis`` is set to ``true`` or the CDK major version is v2. In CDK v1 ``LegacyStackSynthesizer`` is the default if no other synthesizer is specified. Default: - The synthesizer specified on ``App``, or ``DefaultStackSynthesizer`` otherwise.
        :param tags: Stack tags that will be applied to all the taggable resources and the stack itself. Default: {}
        :param termination_protection: Whether to enable termination protection for this stack. Default: false

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c1084d95fded1a099bfe9f522a419270d5befb1d6ad7a10234ddbb6933306b62)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = EntrypointStackProps(
            monitoring=monitoring,
            domain_name=domain_name,
            networking=networking,
            certificate=certificate,
            certificates=certificates,
            entrypoint_name=entrypoint_name,
            entrypoint_security_group_name=entrypoint_security_group_name,
            hosted_zone_props=hosted_zone_props,
            logs_bucket=logs_bucket,
            priority_allocator=priority_allocator,
            security_group_name=security_group_name,
            analytics_reporting=analytics_reporting,
            cross_region_references=cross_region_references,
            description=description,
            env=env,
            permissions_boundary=permissions_boundary,
            stack_name=stack_name,
            suppress_template_indentation=suppress_template_indentation,
            synthesizer=synthesizer,
            tags=tags,
            termination_protection=termination_protection,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="allocateListenerRule")
    def allocate_listener_rule(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        action: typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ListenerAction] = None,
        conditions: typing.Optional[typing.Sequence[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ListenerCondition]] = None,
        priority: typing.Optional[jsii.Number] = None,
        target_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.IApplicationTargetGroup]] = None,
    ) -> _aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ApplicationListenerRule:
        '''(experimental) It creates an ApplicationListenerRule for the HTTPS listener of the Entrypoint.

        This method doesn't require a priority to be explicitly set, and tracks the allocated priorities on a DynamoDB table to avoid conflicts.

        :param scope: -
        :param id: -
        :param action: (experimental) Action to perform when requests are received. Only one of ``action``, ``fixedResponse``, ``redirectResponse`` or ``targetGroups`` can be specified. Default: - No action
        :param conditions: (experimental) Rule applies if matches the conditions. Default: - No conditions.
        :param priority: (experimental) Priority of the rule. The rule with the lowest priority will be used for every request. Default: - The rule will be assigned a priority automatically.
        :param target_groups: (experimental) Target groups to forward requests to. Only one of ``action``, ``fixedResponse``, ``redirectResponse`` or ``targetGroups`` can be specified. Implies a ``forward`` action. Default: - No target groups.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__42ae1e572e15914baf61e548ff4b4cb0bdcc9a6342df5a95deea60cb68f5ae80)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = AllocateApplicationListenerRuleProps(
            action=action,
            conditions=conditions,
            priority=priority,
            target_groups=target_groups,
        )

        return typing.cast(_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ApplicationListenerRule, jsii.invoke(self, "allocateListenerRule", [scope, id, props]))

    @jsii.member(jsii_name="referenceListener")
    def reference_listener(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
    ) -> _aws_cdk_aws_elasticloadbalancingv2_ceddda9d.IApplicationListener:
        '''(experimental) Utility method that returns the HTTPS listener of the entrypoint in a cross-stack compatible way.

        :param scope: -
        :param id: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__180959596e187a102b6b1b0bf499744d61f500a85e4482b590b3d8c42be2feb3)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        return typing.cast(_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.IApplicationListener, jsii.invoke(self, "referenceListener", [scope, id]))

    @builtins.property
    @jsii.member(jsii_name="alb")
    def alb(
        self,
    ) -> _aws_cdk_aws_elasticloadbalancingv2_ceddda9d.IApplicationLoadBalancer:
        '''(experimental) The ALB that serves as the entrypoint.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.IApplicationLoadBalancer, jsii.get(self, "alb"))

    @builtins.property
    @jsii.member(jsii_name="domainName")
    def domain_name(self) -> builtins.str:
        '''(experimental) The load balancer custom domain name.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "domainName"))

    @builtins.property
    @jsii.member(jsii_name="priorityAllocator")
    def priority_allocator(self) -> IApplicationListenerPriorityAllocator:
        '''(experimental) The Application Listener priority allocator for the entrypoint.

        :stability: experimental
        '''
        return typing.cast(IApplicationListenerPriorityAllocator, jsii.get(self, "priorityAllocator"))


__all__ = [
    "AlarmDefinitionProps",
    "AllocateApplicationListenerRuleProps",
    "AllocatePriorityProps",
    "ApplicationListenerPriorityAllocator",
    "ApplicationListenerPriorityAllocatorConfig",
    "ApplicationListenerPriorityAllocatorProps",
    "ApplicationLoadBalancerMonitoringAspect",
    "ApplicationLoadBalancerMonitoringConfig",
    "AuroraCluster",
    "AuroraClusterProps",
    "AuroraClusterStack",
    "AuroraClusterStackProps",
    "BuildAlarmsProps",
    "CacheClusterMonitoringAspect",
    "CacheClusterMonitoringConfig",
    "CloudwatchAlarmsDiscordConfig",
    "CloudwatchAlarmsSlackConfig",
    "CloudwatchAlarmsTopicStack",
    "CloudwatchAlarmsTopicStackProps",
    "DatabaseInstance",
    "DatabaseInstanceProps",
    "DatabaseInstanceStack",
    "DatabaseInstanceStackProps",
    "Entrypoint",
    "EntrypointCertificateProps",
    "EntrypointFromAttributes",
    "EntrypointFromLookupProps",
    "EntrypointProps",
    "EntrypointStack",
    "EntrypointStackProps",
    "FargateServiceMonitoringAspect",
    "FargateServiceMonitoringConfig",
    "IApplicationListenerPriorityAllocator",
    "ICondenseMonitoringFacade",
    "IDatabase",
    "IEntrypoint",
    "INetworking",
    "MonitoringFacade",
    "MonitoringFacadeProps",
    "NaiveBasicAuthCloudfrontFunction",
    "NaiveBasicAuthCloudfrontFunctionExcludedPath",
    "NaiveBasicAuthCloudfrontFunctionProps",
    "Networking",
    "NetworkingProps",
    "NetworkingStack",
    "NetworkingStackProps",
    "RdsClusterMonitoringAspect",
    "RdsClusterMonitoringConfig",
    "RdsInstanceMonitoringAspect",
    "RdsInstanceMonitoringConfig",
    "TargetGroupMonitoringAspect",
    "TargetGroupMonitoringConfig",
    "WidgetAlertAnnotationProps",
]

publication.publish()

def _typecheckingstub__bd29f942ebe15d309286d39cadd5834bfefc30f944e9e7b2839e6cc6464e645a(
    *,
    alarm_id: builtins.str,
    evaluation_periods: jsii.Number,
    metric: _aws_cdk_aws_cloudwatch_ceddda9d.IMetric,
    alarm_description: typing.Optional[builtins.str] = None,
    alarm_name: typing.Optional[builtins.str] = None,
    comparison_operator: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.ComparisonOperator] = None,
    threshold: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0436f7c6595cbd4773aabafb215f9f41c093aca919f108eb93805872a6bbd29d(
    *,
    action: typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ListenerAction] = None,
    conditions: typing.Optional[typing.Sequence[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ListenerCondition]] = None,
    priority: typing.Optional[jsii.Number] = None,
    target_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.IApplicationTargetGroup]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c53d1caad2b9718c58a4ee40428ad65e3e22af09293bdb3bee44acc69f4c2f35(
    *,
    priority: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2ccd5b51a71d2e347bc905ad6ca161e0d2a386f4c98e236c23898f3dc5ee8ebe(
    *,
    priority_initial_value: typing.Optional[jsii.Number] = None,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5f8f953c716556d30741778903d495459a7f78be63d2a85ee17f15f7a6085ab1(
    *,
    priority_initial_value: typing.Optional[jsii.Number] = None,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    listener: _aws_cdk_aws_elasticloadbalancingv2_ceddda9d.IApplicationListener,
    priority_allocator_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__21c7d9d40cf1792a68c47202afcaf8e6c3fdb61ac00ad196a604414b9783713c(
    monitoring_facade: ICondenseMonitoringFacade,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1cfa6dfa414bbd2287d047457d1e08f1c4f343fe957a79584fa8db8884bab20d(
    node: _aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ApplicationLoadBalancer,
    *,
    redirect_url_limit_exceeded_threshold: typing.Optional[jsii.Number] = None,
    rejected_connections_threshold: typing.Optional[jsii.Number] = None,
    response_time_threshold: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    target5xx_errors_threshold: typing.Optional[jsii.Number] = None,
    target_connection_errors_threshold: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a315fe0f4105c7a383fb140d4165db45a3067371dbf51d7eb6f3fe7bd8166048(
    node: _constructs_77d1e7e8.IConstruct,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cea2a4cc207c22c7090a74b53d8a6cbf6a69051c06e1e404fb043435049a4a1a(
    *,
    redirect_url_limit_exceeded_threshold: typing.Optional[jsii.Number] = None,
    rejected_connections_threshold: typing.Optional[jsii.Number] = None,
    response_time_threshold: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    target5xx_errors_threshold: typing.Optional[jsii.Number] = None,
    target_connection_errors_threshold: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e574b5d10e1d847dabe15ebbbc4935b04c4f2cbd8a36b95cdb4526ea5fbf9956(
    *,
    engine: _aws_cdk_aws_rds_ceddda9d.IClusterEngine,
    networking: INetworking,
    backup_retention: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    cloudwatch_logs_exports: typing.Optional[typing.Sequence[builtins.str]] = None,
    cloudwatch_logs_retention: typing.Optional[_aws_cdk_aws_logs_ceddda9d.RetentionDays] = None,
    cluster_identifier: typing.Optional[builtins.str] = None,
    cluster_parameters: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    credentials_secret_name: typing.Optional[builtins.str] = None,
    credentials_username: typing.Optional[builtins.str] = None,
    database_name: typing.Optional[builtins.str] = None,
    instance_parameters: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    parameters: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    readers: typing.Optional[typing.Sequence[_aws_cdk_aws_rds_ceddda9d.IClusterInstance]] = None,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    security_group_name: typing.Optional[builtins.str] = None,
    writer: typing.Optional[_aws_cdk_aws_rds_ceddda9d.IClusterInstance] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d7e4ee724edadf6dd8693e56cd66d90d5cba69a05ad5791d1271729d01dabc4c(
    *,
    engine: _aws_cdk_aws_rds_ceddda9d.IClusterEngine,
    networking: INetworking,
    backup_retention: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    cloudwatch_logs_exports: typing.Optional[typing.Sequence[builtins.str]] = None,
    cloudwatch_logs_retention: typing.Optional[_aws_cdk_aws_logs_ceddda9d.RetentionDays] = None,
    cluster_identifier: typing.Optional[builtins.str] = None,
    cluster_parameters: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    credentials_secret_name: typing.Optional[builtins.str] = None,
    credentials_username: typing.Optional[builtins.str] = None,
    database_name: typing.Optional[builtins.str] = None,
    instance_parameters: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    parameters: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    readers: typing.Optional[typing.Sequence[_aws_cdk_aws_rds_ceddda9d.IClusterInstance]] = None,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    security_group_name: typing.Optional[builtins.str] = None,
    writer: typing.Optional[_aws_cdk_aws_rds_ceddda9d.IClusterInstance] = None,
    analytics_reporting: typing.Optional[builtins.bool] = None,
    cross_region_references: typing.Optional[builtins.bool] = None,
    description: typing.Optional[builtins.str] = None,
    env: typing.Optional[typing.Union[_aws_cdk_ceddda9d.Environment, typing.Dict[builtins.str, typing.Any]]] = None,
    permissions_boundary: typing.Optional[_aws_cdk_ceddda9d.PermissionsBoundary] = None,
    stack_name: typing.Optional[builtins.str] = None,
    suppress_template_indentation: typing.Optional[builtins.bool] = None,
    synthesizer: typing.Optional[_aws_cdk_ceddda9d.IStackSynthesizer] = None,
    tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    termination_protection: typing.Optional[builtins.bool] = None,
    monitoring: typing.Optional[typing.Union[MonitoringFacadeProps, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8bce0c670e92bd5df1aea2a72a8b2611d5c35bac73dcaba00625e9d792bd3492(
    *,
    alarms: typing.Sequence[typing.Union[AlarmDefinitionProps, typing.Dict[builtins.str, typing.Any]]],
    node: _constructs_77d1e7e8.Construct,
    node_identifier: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7aef7e87980576bf6891799025cab53dd237cb096ccf028905894401b9349a54(
    monitoring_facade: ICondenseMonitoringFacade,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5d896e278ec33d0cf2074937f796f239b7fb8aa49653a46b2f3f4401b5ae50f8(
    node: _aws_cdk_aws_elasticache_ceddda9d.CfnCacheCluster,
    *,
    cpu_utilization_threshold: typing.Optional[jsii.Number] = None,
    engine_cpu_utilization_threshold: typing.Optional[jsii.Number] = None,
    max_connections_threshold: typing.Optional[jsii.Number] = None,
    memory_usage_threshold: typing.Optional[jsii.Number] = None,
    replication_lag_threshold: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b4e5b66f2c71a825830e5ce1ed16e411bf5446d194055bcdfe8ca31aadcf4636(
    node: _constructs_77d1e7e8.IConstruct,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f100edbfc1c3c6e516f7c9dd96a162cd991c46b41383cc0777180f44158595d8(
    *,
    cpu_utilization_threshold: typing.Optional[jsii.Number] = None,
    engine_cpu_utilization_threshold: typing.Optional[jsii.Number] = None,
    max_connections_threshold: typing.Optional[jsii.Number] = None,
    memory_usage_threshold: typing.Optional[jsii.Number] = None,
    replication_lag_threshold: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fdcb0b643b2fafd341022ee345eb921ce9f29aac668330e8eb0f5a143a0a022a(
    *,
    webhook: builtins.str,
    username: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ca263c8f4b8475c5c6b12308ef78c8e38b325e08b9bd3ae58cb8e3a5cbb048c4(
    *,
    webhook: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__57113cf1eb8b5583f1a3b8b5ff0d2aee0a6d1775e0fbb261cde6c8e9cfcd835d(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    discord: typing.Optional[typing.Union[CloudwatchAlarmsDiscordConfig, typing.Dict[builtins.str, typing.Any]]] = None,
    jira_subscription_webhook: typing.Optional[builtins.str] = None,
    slack: typing.Optional[typing.Union[CloudwatchAlarmsSlackConfig, typing.Dict[builtins.str, typing.Any]]] = None,
    topic_name: typing.Optional[builtins.str] = None,
    url_subscription_webhooks: typing.Optional[typing.Sequence[builtins.str]] = None,
    analytics_reporting: typing.Optional[builtins.bool] = None,
    cross_region_references: typing.Optional[builtins.bool] = None,
    description: typing.Optional[builtins.str] = None,
    env: typing.Optional[typing.Union[_aws_cdk_ceddda9d.Environment, typing.Dict[builtins.str, typing.Any]]] = None,
    permissions_boundary: typing.Optional[_aws_cdk_ceddda9d.PermissionsBoundary] = None,
    stack_name: typing.Optional[builtins.str] = None,
    suppress_template_indentation: typing.Optional[builtins.bool] = None,
    synthesizer: typing.Optional[_aws_cdk_ceddda9d.IStackSynthesizer] = None,
    tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    termination_protection: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0681772f7ea86b94082174f0e8837e8be9423519730e5fb2d137a83caaa8503d(
    *,
    analytics_reporting: typing.Optional[builtins.bool] = None,
    cross_region_references: typing.Optional[builtins.bool] = None,
    description: typing.Optional[builtins.str] = None,
    env: typing.Optional[typing.Union[_aws_cdk_ceddda9d.Environment, typing.Dict[builtins.str, typing.Any]]] = None,
    permissions_boundary: typing.Optional[_aws_cdk_ceddda9d.PermissionsBoundary] = None,
    stack_name: typing.Optional[builtins.str] = None,
    suppress_template_indentation: typing.Optional[builtins.bool] = None,
    synthesizer: typing.Optional[_aws_cdk_ceddda9d.IStackSynthesizer] = None,
    tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    termination_protection: typing.Optional[builtins.bool] = None,
    discord: typing.Optional[typing.Union[CloudwatchAlarmsDiscordConfig, typing.Dict[builtins.str, typing.Any]]] = None,
    jira_subscription_webhook: typing.Optional[builtins.str] = None,
    slack: typing.Optional[typing.Union[CloudwatchAlarmsSlackConfig, typing.Dict[builtins.str, typing.Any]]] = None,
    topic_name: typing.Optional[builtins.str] = None,
    url_subscription_webhooks: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a7e78fb9d1c1440969aaea6b5f1207d42b7080de9a6db81dca390dd6232c8cf9(
    *,
    engine: _aws_cdk_aws_rds_ceddda9d.IInstanceEngine,
    networking: INetworking,
    allocated_storage: typing.Optional[jsii.Number] = None,
    allow_major_version_upgrade: typing.Optional[builtins.bool] = None,
    backup_retention: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    cloudwatch_logs_exports: typing.Optional[typing.Sequence[builtins.str]] = None,
    cloudwatch_logs_retention: typing.Optional[_aws_cdk_aws_logs_ceddda9d.RetentionDays] = None,
    credentials_secret_name: typing.Optional[builtins.str] = None,
    credentials_username: typing.Optional[builtins.str] = None,
    database_name: typing.Optional[builtins.str] = None,
    enable_performance_insights: typing.Optional[builtins.bool] = None,
    instance_identifier: typing.Optional[builtins.str] = None,
    instance_type: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.InstanceType] = None,
    max_allocated_storage: typing.Optional[jsii.Number] = None,
    multi_az: typing.Optional[builtins.bool] = None,
    parameters: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    security_group_name: typing.Optional[builtins.str] = None,
    storage_type: typing.Optional[_aws_cdk_aws_rds_ceddda9d.StorageType] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__78f8facc5fb08045f0a685c1db7239710d0c81292514a8db2855f969f9697d10(
    *,
    engine: _aws_cdk_aws_rds_ceddda9d.IInstanceEngine,
    networking: INetworking,
    allocated_storage: typing.Optional[jsii.Number] = None,
    allow_major_version_upgrade: typing.Optional[builtins.bool] = None,
    backup_retention: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    cloudwatch_logs_exports: typing.Optional[typing.Sequence[builtins.str]] = None,
    cloudwatch_logs_retention: typing.Optional[_aws_cdk_aws_logs_ceddda9d.RetentionDays] = None,
    credentials_secret_name: typing.Optional[builtins.str] = None,
    credentials_username: typing.Optional[builtins.str] = None,
    database_name: typing.Optional[builtins.str] = None,
    enable_performance_insights: typing.Optional[builtins.bool] = None,
    instance_identifier: typing.Optional[builtins.str] = None,
    instance_type: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.InstanceType] = None,
    max_allocated_storage: typing.Optional[jsii.Number] = None,
    multi_az: typing.Optional[builtins.bool] = None,
    parameters: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    security_group_name: typing.Optional[builtins.str] = None,
    storage_type: typing.Optional[_aws_cdk_aws_rds_ceddda9d.StorageType] = None,
    analytics_reporting: typing.Optional[builtins.bool] = None,
    cross_region_references: typing.Optional[builtins.bool] = None,
    description: typing.Optional[builtins.str] = None,
    env: typing.Optional[typing.Union[_aws_cdk_ceddda9d.Environment, typing.Dict[builtins.str, typing.Any]]] = None,
    permissions_boundary: typing.Optional[_aws_cdk_ceddda9d.PermissionsBoundary] = None,
    stack_name: typing.Optional[builtins.str] = None,
    suppress_template_indentation: typing.Optional[builtins.bool] = None,
    synthesizer: typing.Optional[_aws_cdk_ceddda9d.IStackSynthesizer] = None,
    tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    termination_protection: typing.Optional[builtins.bool] = None,
    monitoring: typing.Optional[typing.Union[MonitoringFacadeProps, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e5e0795d189370067efff1cf7b82e81499224af835fb61b6505603886fd34217(
    *,
    certificate: typing.Optional[_aws_cdk_aws_certificatemanager_ceddda9d.ICertificate] = None,
    certificate_arn: typing.Optional[builtins.str] = None,
    wildcard_certificate: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8c3bfc299e27a3860e607664a4c27cda4af08536297db566a2b2aedc708f3b8b(
    *,
    listener_arn: builtins.str,
    load_balancer_arn: builtins.str,
    security_group_id: builtins.str,
    domain_name: typing.Optional[builtins.str] = None,
    entrypoint_name: typing.Optional[builtins.str] = None,
    priority_allocator_service_token: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6d6cd06c158bbf007dcd6d881c99b7e87d281495cface2615f9a39294352c91f(
    *,
    entrypoint_name: builtins.str,
    domain_name: typing.Optional[builtins.str] = None,
    vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
    vpc_lookup: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.VpcLookupOptions, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__83a61ef01fb98c7353c39945cc7c3dcb1c823185ce1714ad3ca8e84636eaec89(
    *,
    domain_name: builtins.str,
    networking: INetworking,
    certificate: typing.Optional[typing.Union[EntrypointCertificateProps, typing.Dict[builtins.str, typing.Any]]] = None,
    certificates: typing.Optional[typing.Sequence[typing.Union[EntrypointCertificateProps, typing.Dict[builtins.str, typing.Any]]]] = None,
    entrypoint_name: typing.Optional[builtins.str] = None,
    entrypoint_security_group_name: typing.Optional[builtins.str] = None,
    hosted_zone_props: typing.Optional[typing.Union[_aws_cdk_aws_route53_ceddda9d.HostedZoneAttributes, typing.Dict[builtins.str, typing.Any]]] = None,
    logs_bucket: typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket] = None,
    priority_allocator: typing.Optional[typing.Union[ApplicationListenerPriorityAllocatorConfig, typing.Dict[builtins.str, typing.Any]]] = None,
    security_group_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c85f5510b68e3824ed823dfefbd0ed33f8c7fb08af1202ef020e1e4b69f543d0(
    *,
    domain_name: builtins.str,
    networking: INetworking,
    certificate: typing.Optional[typing.Union[EntrypointCertificateProps, typing.Dict[builtins.str, typing.Any]]] = None,
    certificates: typing.Optional[typing.Sequence[typing.Union[EntrypointCertificateProps, typing.Dict[builtins.str, typing.Any]]]] = None,
    entrypoint_name: typing.Optional[builtins.str] = None,
    entrypoint_security_group_name: typing.Optional[builtins.str] = None,
    hosted_zone_props: typing.Optional[typing.Union[_aws_cdk_aws_route53_ceddda9d.HostedZoneAttributes, typing.Dict[builtins.str, typing.Any]]] = None,
    logs_bucket: typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket] = None,
    priority_allocator: typing.Optional[typing.Union[ApplicationListenerPriorityAllocatorConfig, typing.Dict[builtins.str, typing.Any]]] = None,
    security_group_name: typing.Optional[builtins.str] = None,
    analytics_reporting: typing.Optional[builtins.bool] = None,
    cross_region_references: typing.Optional[builtins.bool] = None,
    description: typing.Optional[builtins.str] = None,
    env: typing.Optional[typing.Union[_aws_cdk_ceddda9d.Environment, typing.Dict[builtins.str, typing.Any]]] = None,
    permissions_boundary: typing.Optional[_aws_cdk_ceddda9d.PermissionsBoundary] = None,
    stack_name: typing.Optional[builtins.str] = None,
    suppress_template_indentation: typing.Optional[builtins.bool] = None,
    synthesizer: typing.Optional[_aws_cdk_ceddda9d.IStackSynthesizer] = None,
    tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    termination_protection: typing.Optional[builtins.bool] = None,
    monitoring: typing.Optional[typing.Union[MonitoringFacadeProps, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__630a342639fde7b8ddb7831e15c20bce6ca1d01d8e73643086815dda564a37af(
    monitoring_facade: ICondenseMonitoringFacade,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__08198ad4b3ada58ccbada9a586c23f0188d9bf3860baa47d1c58eb748e16020f(
    node: _aws_cdk_aws_ecs_ceddda9d.FargateService,
    *,
    cpu_utilization_threshold: typing.Optional[jsii.Number] = None,
    memory_utilization: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a5bf7c35fcf655cb700cb96318322e89f7fdcaae7658ed9df49af27c86903a83(
    node: _constructs_77d1e7e8.IConstruct,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5d9c95dc69a12f04e36f92d0cb68fcee773eb13b67f2286aae9b9484c660ca8b(
    *,
    cpu_utilization_threshold: typing.Optional[jsii.Number] = None,
    memory_utilization: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__81990a8032fc66ef4e810f42acc7e5d213a2914b89e2cdee1ba98e0eea19d6bb(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    priority: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ae0302a7c36b248336045bd8c22ffdffd2a485c1a8b47c60c0ce68946566b028(
    alarm: _aws_cdk_aws_cloudwatch_ceddda9d.Alarm,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2987d0fa60464de1815bbddfeb2c93d14ecf75f24cf21f876ac433bfda2c54a6(
    scope: _constructs_77d1e7e8.Construct,
    id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4008bd74f518e6bfa2d805893a8dde6ba0d0f034c8d31f73351f2c31441f556b(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    action: typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ListenerAction] = None,
    conditions: typing.Optional[typing.Sequence[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ListenerCondition]] = None,
    priority: typing.Optional[jsii.Number] = None,
    target_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.IApplicationTargetGroup]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__02f32d7fdaba44b683a7d540d6ef577e3716c742002e81f804746bc7973e65fa(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5b60432f85a285be42a21b1122e88974bc2b20a98b76d5e0ee45cf7af2cd144e(
    scope: _aws_cdk_ceddda9d.Stack,
    *,
    topic_arn: builtins.str,
    dashboard_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__062fb685fcb23a28ff48a011c2571420172c27726b513c0a6b3319958ed71380(
    scope: _constructs_77d1e7e8.Construct,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dcb66ac5e0587112880aa0994495745143d5d9118d1dda39610f56b7520fea2d(
    alarm: _aws_cdk_aws_cloudwatch_ceddda9d.Alarm,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__da7e650bffb023ec1deaa3822cc1807824bfbea19fe8bd4d8e9c1befa0714e5d(
    resource: _aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ApplicationLoadBalancer,
    *,
    redirect_url_limit_exceeded_threshold: typing.Optional[jsii.Number] = None,
    rejected_connections_threshold: typing.Optional[jsii.Number] = None,
    response_time_threshold: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    target5xx_errors_threshold: typing.Optional[jsii.Number] = None,
    target_connection_errors_threshold: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__77ae16eef5ef965347724604827c8f4ef09950c27eb1383a996fc45847172b85(
    resource: _aws_cdk_aws_elasticache_ceddda9d.CfnCacheCluster,
    *,
    cpu_utilization_threshold: typing.Optional[jsii.Number] = None,
    engine_cpu_utilization_threshold: typing.Optional[jsii.Number] = None,
    max_connections_threshold: typing.Optional[jsii.Number] = None,
    memory_usage_threshold: typing.Optional[jsii.Number] = None,
    replication_lag_threshold: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cc5797e8af3aea6b37a46a23ca01873dd31f7c7f1fd5d8d4c5329140146598af(
    resource: _aws_cdk_aws_ecs_ceddda9d.FargateService,
    *,
    cpu_utilization_threshold: typing.Optional[jsii.Number] = None,
    memory_utilization: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__04d4a4a7106da61f61e3c6b31bd24cfe6700fe524ec7109cd343ec0d17386af1(
    resource: _aws_cdk_aws_rds_ceddda9d.DatabaseCluster,
    *,
    cpu_utilization_threshold: typing.Optional[jsii.Number] = None,
    ebs_byte_balance_threshold: typing.Optional[jsii.Number] = None,
    ebs_io_balance_threshold: typing.Optional[jsii.Number] = None,
    freeable_memory_threshold: typing.Optional[_aws_cdk_ceddda9d.Size] = None,
    max_connections_threshold: typing.Optional[jsii.Number] = None,
    read_latency_threshold: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e6ca11cc84243de70b6f802cf22bd5a857a72dd9ee192b19d200ea6908f75205(
    resource: _aws_cdk_aws_rds_ceddda9d.DatabaseInstance,
    *,
    cpu_utilization_threshold: typing.Optional[jsii.Number] = None,
    ebs_byte_balance_threshold: typing.Optional[jsii.Number] = None,
    ebs_io_balance_threshold: typing.Optional[jsii.Number] = None,
    freeable_memory_threshold: typing.Optional[_aws_cdk_ceddda9d.Size] = None,
    free_storage_space_threshold: typing.Optional[_aws_cdk_ceddda9d.Size] = None,
    max_connections_threshold: typing.Optional[jsii.Number] = None,
    read_latency_threshold: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cbda6ebd99f677bf0faefa48f330959fb4c1e31fbc4ef282ced8cb8a8312f7d8(
    resource: _aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ApplicationTargetGroup,
    *,
    min_healthy_hosts_threshold: typing.Optional[jsii.Number] = None,
    response_time_threshold: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__24412f7336ded0c019fb4a3d9571528862b33059004b84acdee1f6ddefaf66e1(
    *,
    topic_arn: builtins.str,
    dashboard_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2a83db3b7239cac1a1fa2230e335342bae58153ab2fb6a02426375af19d34898(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    basic_auth_string: builtins.str,
    exclude_paths: typing.Optional[typing.Sequence[typing.Union[NaiveBasicAuthCloudfrontFunctionExcludedPath, typing.Dict[builtins.str, typing.Any]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2d7ee86e24b43210088ff0e7d04520ac486945cb13c7906b88b1b91a7e740d50(
    *,
    path: builtins.str,
    match_mode: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__35170ecaf31393ae4e535e7b932855526964579db38be7b84aa1931339ceea19(
    *,
    basic_auth_string: builtins.str,
    exclude_paths: typing.Optional[typing.Sequence[typing.Union[NaiveBasicAuthCloudfrontFunctionExcludedPath, typing.Dict[builtins.str, typing.Any]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9333f69a8b9c318ec7120273e8700bfc06f052d41e91c864702225cd0e11efdb(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    ip_addresses: _aws_cdk_aws_ec2_ceddda9d.IIpAddresses,
    bastion_host_ami: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IMachineImage] = None,
    bastion_host_enabled: typing.Optional[builtins.bool] = None,
    bastion_host_instance_type: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.InstanceType] = None,
    bastion_name: typing.Optional[builtins.str] = None,
    max_azs: typing.Optional[jsii.Number] = None,
    nat_gateways: typing.Optional[jsii.Number] = None,
    vpc_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__76cefbe0036052e6c98f7dd510a4c421bbbf507fe910b749b221863b80be96ab(
    *,
    ip_addresses: _aws_cdk_aws_ec2_ceddda9d.IIpAddresses,
    bastion_host_ami: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IMachineImage] = None,
    bastion_host_enabled: typing.Optional[builtins.bool] = None,
    bastion_host_instance_type: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.InstanceType] = None,
    bastion_name: typing.Optional[builtins.str] = None,
    max_azs: typing.Optional[jsii.Number] = None,
    nat_gateways: typing.Optional[jsii.Number] = None,
    vpc_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3a3f5da197e1af45028448ba5f94d78977c95ec2ad500d29b674d835d5c6a638(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    ip_addresses: _aws_cdk_aws_ec2_ceddda9d.IIpAddresses,
    bastion_host_ami: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IMachineImage] = None,
    bastion_host_enabled: typing.Optional[builtins.bool] = None,
    bastion_host_instance_type: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.InstanceType] = None,
    bastion_name: typing.Optional[builtins.str] = None,
    max_azs: typing.Optional[jsii.Number] = None,
    nat_gateways: typing.Optional[jsii.Number] = None,
    vpc_name: typing.Optional[builtins.str] = None,
    analytics_reporting: typing.Optional[builtins.bool] = None,
    cross_region_references: typing.Optional[builtins.bool] = None,
    description: typing.Optional[builtins.str] = None,
    env: typing.Optional[typing.Union[_aws_cdk_ceddda9d.Environment, typing.Dict[builtins.str, typing.Any]]] = None,
    permissions_boundary: typing.Optional[_aws_cdk_ceddda9d.PermissionsBoundary] = None,
    stack_name: typing.Optional[builtins.str] = None,
    suppress_template_indentation: typing.Optional[builtins.bool] = None,
    synthesizer: typing.Optional[_aws_cdk_ceddda9d.IStackSynthesizer] = None,
    tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    termination_protection: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0b485658e30a4cd992bcabfcfa062a6820180ada5dd60554fa23d944cee8f6f3(
    *,
    ip_addresses: _aws_cdk_aws_ec2_ceddda9d.IIpAddresses,
    bastion_host_ami: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IMachineImage] = None,
    bastion_host_enabled: typing.Optional[builtins.bool] = None,
    bastion_host_instance_type: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.InstanceType] = None,
    bastion_name: typing.Optional[builtins.str] = None,
    max_azs: typing.Optional[jsii.Number] = None,
    nat_gateways: typing.Optional[jsii.Number] = None,
    vpc_name: typing.Optional[builtins.str] = None,
    analytics_reporting: typing.Optional[builtins.bool] = None,
    cross_region_references: typing.Optional[builtins.bool] = None,
    description: typing.Optional[builtins.str] = None,
    env: typing.Optional[typing.Union[_aws_cdk_ceddda9d.Environment, typing.Dict[builtins.str, typing.Any]]] = None,
    permissions_boundary: typing.Optional[_aws_cdk_ceddda9d.PermissionsBoundary] = None,
    stack_name: typing.Optional[builtins.str] = None,
    suppress_template_indentation: typing.Optional[builtins.bool] = None,
    synthesizer: typing.Optional[_aws_cdk_ceddda9d.IStackSynthesizer] = None,
    tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    termination_protection: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4aca2c196ab1077acc3c53fe795c33684b2b614468023689c3a055c3f9b492c5(
    monitoring_facade: ICondenseMonitoringFacade,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a5f22f24629398f744a2a08eb4f5377bd7a3b6b6f99cc28ac4c3928736022f1d(
    node: _aws_cdk_aws_rds_ceddda9d.DatabaseCluster,
    *,
    cpu_utilization_threshold: typing.Optional[jsii.Number] = None,
    ebs_byte_balance_threshold: typing.Optional[jsii.Number] = None,
    ebs_io_balance_threshold: typing.Optional[jsii.Number] = None,
    freeable_memory_threshold: typing.Optional[_aws_cdk_ceddda9d.Size] = None,
    max_connections_threshold: typing.Optional[jsii.Number] = None,
    read_latency_threshold: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__20d91c6ae5b029b42be80d506f3b6044ae0bf016b7daa8e33d8c6d4b0143c20b(
    node: _constructs_77d1e7e8.IConstruct,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eca8553b2bbcadedc0bc66ed7c18f8470da2dc0dc250714df2eda482318e71ea(
    *,
    cpu_utilization_threshold: typing.Optional[jsii.Number] = None,
    ebs_byte_balance_threshold: typing.Optional[jsii.Number] = None,
    ebs_io_balance_threshold: typing.Optional[jsii.Number] = None,
    freeable_memory_threshold: typing.Optional[_aws_cdk_ceddda9d.Size] = None,
    max_connections_threshold: typing.Optional[jsii.Number] = None,
    read_latency_threshold: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__93469445a9438705a1bedc45123357e71bf0034dd3957f7c851bd8caad946f2a(
    monitoring_facade: ICondenseMonitoringFacade,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bf21bc988337443e51be3192cdb0b1135c9f5c2d3b9581366b89ae59cd3ef8db(
    node: _aws_cdk_aws_rds_ceddda9d.DatabaseInstance,
    *,
    cpu_utilization_threshold: typing.Optional[jsii.Number] = None,
    ebs_byte_balance_threshold: typing.Optional[jsii.Number] = None,
    ebs_io_balance_threshold: typing.Optional[jsii.Number] = None,
    freeable_memory_threshold: typing.Optional[_aws_cdk_ceddda9d.Size] = None,
    free_storage_space_threshold: typing.Optional[_aws_cdk_ceddda9d.Size] = None,
    max_connections_threshold: typing.Optional[jsii.Number] = None,
    read_latency_threshold: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f2d14017d7e7fd1f9ed75765544e708efbd58aeb885da78632062a5b2cd16ad0(
    node: _constructs_77d1e7e8.IConstruct,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2d08db96b75dd7234176dfe2c64e7ae1bedc0d3bb341bb1db6375b0b1f865b05(
    *,
    cpu_utilization_threshold: typing.Optional[jsii.Number] = None,
    ebs_byte_balance_threshold: typing.Optional[jsii.Number] = None,
    ebs_io_balance_threshold: typing.Optional[jsii.Number] = None,
    freeable_memory_threshold: typing.Optional[_aws_cdk_ceddda9d.Size] = None,
    free_storage_space_threshold: typing.Optional[_aws_cdk_ceddda9d.Size] = None,
    max_connections_threshold: typing.Optional[jsii.Number] = None,
    read_latency_threshold: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__24955513de57d1b7cc9c76f39b7d30a926cd40697184c043fafc5ad4cbd9c667(
    monitoring_facade: ICondenseMonitoringFacade,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a1b1e908a3fff25a3d0a4d7e4611154465b0d84ff11973cf045225e068bae815(
    node: _aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ApplicationTargetGroup,
    *,
    min_healthy_hosts_threshold: typing.Optional[jsii.Number] = None,
    response_time_threshold: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3817ebef06ec180d4a607f13776609a70965bf3b9ca0e264b5d069f374321ce3(
    node: _constructs_77d1e7e8.IConstruct,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b0784d38b49ed7fc47c445cbd6441a0407e25d837cf3420f648b86f634b852a7(
    *,
    min_healthy_hosts_threshold: typing.Optional[jsii.Number] = None,
    response_time_threshold: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__89455bf6261146031cb64d0d28df64ec214bc886d3f0b46b21c4af67b56515fa(
    *,
    color: typing.Optional[builtins.str] = None,
    label: typing.Optional[builtins.str] = None,
    value: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f0b33f5852f61e5ad80aa8bc6b8b8a0774fe53a25aeaabb7e6d326db7c403611(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    listener: _aws_cdk_aws_elasticloadbalancingv2_ceddda9d.IApplicationListener,
    priority_allocator_name: typing.Optional[builtins.str] = None,
    priority_initial_value: typing.Optional[jsii.Number] = None,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2cb22ab7d0fc51835785d6267c6699520e6284504956a924e3d48a825c1262a0(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    priority_allocator_name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ee5c94b5aeea053e8d5ce67f8781663bf3f44a9dde6c2719ff5b230c40b79c3d(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    service_token: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e7d93e36d219bbbffd02e9ec5ef687591aab7747ad6ccacd73bebd3519fad280(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    priority: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__918e480e1b8c0172af87f81e840b4c6d9c58fba4979dc3a0c448041c4ee1d3b4(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    engine: _aws_cdk_aws_rds_ceddda9d.IClusterEngine,
    networking: INetworking,
    backup_retention: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    cloudwatch_logs_exports: typing.Optional[typing.Sequence[builtins.str]] = None,
    cloudwatch_logs_retention: typing.Optional[_aws_cdk_aws_logs_ceddda9d.RetentionDays] = None,
    cluster_identifier: typing.Optional[builtins.str] = None,
    cluster_parameters: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    credentials_secret_name: typing.Optional[builtins.str] = None,
    credentials_username: typing.Optional[builtins.str] = None,
    database_name: typing.Optional[builtins.str] = None,
    instance_parameters: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    parameters: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    readers: typing.Optional[typing.Sequence[_aws_cdk_aws_rds_ceddda9d.IClusterInstance]] = None,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    security_group_name: typing.Optional[builtins.str] = None,
    writer: typing.Optional[_aws_cdk_aws_rds_ceddda9d.IClusterInstance] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__675175b6caee5dfd5a620ef07239855087edc66870da74eb996e1d64a1c4a323(
    engine: _aws_cdk_aws_rds_ceddda9d.IClusterEngine,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5dffd8835158ac1142b018590ae1cc477906ec915c970cb7432434404f019e0f(
    scope: _constructs_77d1e7e8.Construct,
    id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cda33e503703b48b6026ca8d22c2708577a44c705b8a13324c75fa6c5337dd0a(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    monitoring: typing.Optional[typing.Union[MonitoringFacadeProps, typing.Dict[builtins.str, typing.Any]]] = None,
    engine: _aws_cdk_aws_rds_ceddda9d.IClusterEngine,
    networking: INetworking,
    backup_retention: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    cloudwatch_logs_exports: typing.Optional[typing.Sequence[builtins.str]] = None,
    cloudwatch_logs_retention: typing.Optional[_aws_cdk_aws_logs_ceddda9d.RetentionDays] = None,
    cluster_identifier: typing.Optional[builtins.str] = None,
    cluster_parameters: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    credentials_secret_name: typing.Optional[builtins.str] = None,
    credentials_username: typing.Optional[builtins.str] = None,
    database_name: typing.Optional[builtins.str] = None,
    instance_parameters: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    parameters: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    readers: typing.Optional[typing.Sequence[_aws_cdk_aws_rds_ceddda9d.IClusterInstance]] = None,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    security_group_name: typing.Optional[builtins.str] = None,
    writer: typing.Optional[_aws_cdk_aws_rds_ceddda9d.IClusterInstance] = None,
    analytics_reporting: typing.Optional[builtins.bool] = None,
    cross_region_references: typing.Optional[builtins.bool] = None,
    description: typing.Optional[builtins.str] = None,
    env: typing.Optional[typing.Union[_aws_cdk_ceddda9d.Environment, typing.Dict[builtins.str, typing.Any]]] = None,
    permissions_boundary: typing.Optional[_aws_cdk_ceddda9d.PermissionsBoundary] = None,
    stack_name: typing.Optional[builtins.str] = None,
    suppress_template_indentation: typing.Optional[builtins.bool] = None,
    synthesizer: typing.Optional[_aws_cdk_ceddda9d.IStackSynthesizer] = None,
    tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    termination_protection: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8992950dcef6a8a7769c27b826324c48b64ebe4c26e220e72fa33671b315ee04(
    scope: _constructs_77d1e7e8.Construct,
    id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0140b7dc73cbbd21efe34e542cab574c9dd014c3f5aa2cdd846b759a05a95a0e(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    engine: _aws_cdk_aws_rds_ceddda9d.IInstanceEngine,
    networking: INetworking,
    allocated_storage: typing.Optional[jsii.Number] = None,
    allow_major_version_upgrade: typing.Optional[builtins.bool] = None,
    backup_retention: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    cloudwatch_logs_exports: typing.Optional[typing.Sequence[builtins.str]] = None,
    cloudwatch_logs_retention: typing.Optional[_aws_cdk_aws_logs_ceddda9d.RetentionDays] = None,
    credentials_secret_name: typing.Optional[builtins.str] = None,
    credentials_username: typing.Optional[builtins.str] = None,
    database_name: typing.Optional[builtins.str] = None,
    enable_performance_insights: typing.Optional[builtins.bool] = None,
    instance_identifier: typing.Optional[builtins.str] = None,
    instance_type: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.InstanceType] = None,
    max_allocated_storage: typing.Optional[jsii.Number] = None,
    multi_az: typing.Optional[builtins.bool] = None,
    parameters: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    security_group_name: typing.Optional[builtins.str] = None,
    storage_type: typing.Optional[_aws_cdk_aws_rds_ceddda9d.StorageType] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b66785938111d23423861844f79752b5d1db28e61ea7a8bd09083c65704b9826(
    scope: _constructs_77d1e7e8.Construct,
    id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0a3c3637d08962f782b0f4015419c22e4d8fd0d21f593f42460e5ceb6df442e2(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    monitoring: typing.Optional[typing.Union[MonitoringFacadeProps, typing.Dict[builtins.str, typing.Any]]] = None,
    engine: _aws_cdk_aws_rds_ceddda9d.IInstanceEngine,
    networking: INetworking,
    allocated_storage: typing.Optional[jsii.Number] = None,
    allow_major_version_upgrade: typing.Optional[builtins.bool] = None,
    backup_retention: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    cloudwatch_logs_exports: typing.Optional[typing.Sequence[builtins.str]] = None,
    cloudwatch_logs_retention: typing.Optional[_aws_cdk_aws_logs_ceddda9d.RetentionDays] = None,
    credentials_secret_name: typing.Optional[builtins.str] = None,
    credentials_username: typing.Optional[builtins.str] = None,
    database_name: typing.Optional[builtins.str] = None,
    enable_performance_insights: typing.Optional[builtins.bool] = None,
    instance_identifier: typing.Optional[builtins.str] = None,
    instance_type: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.InstanceType] = None,
    max_allocated_storage: typing.Optional[jsii.Number] = None,
    multi_az: typing.Optional[builtins.bool] = None,
    parameters: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    security_group_name: typing.Optional[builtins.str] = None,
    storage_type: typing.Optional[_aws_cdk_aws_rds_ceddda9d.StorageType] = None,
    analytics_reporting: typing.Optional[builtins.bool] = None,
    cross_region_references: typing.Optional[builtins.bool] = None,
    description: typing.Optional[builtins.str] = None,
    env: typing.Optional[typing.Union[_aws_cdk_ceddda9d.Environment, typing.Dict[builtins.str, typing.Any]]] = None,
    permissions_boundary: typing.Optional[_aws_cdk_ceddda9d.PermissionsBoundary] = None,
    stack_name: typing.Optional[builtins.str] = None,
    suppress_template_indentation: typing.Optional[builtins.bool] = None,
    synthesizer: typing.Optional[_aws_cdk_ceddda9d.IStackSynthesizer] = None,
    tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    termination_protection: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__23f0915d15304e34335fbfdb975e4739d91e3b735de6d3222d3eb061eb7e6340(
    scope: _constructs_77d1e7e8.Construct,
    id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__43117885de9d29986a3fba3fd54947e369ad7fcb99dfbb6e11b21e69a743eb0f(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    domain_name: builtins.str,
    networking: INetworking,
    certificate: typing.Optional[typing.Union[EntrypointCertificateProps, typing.Dict[builtins.str, typing.Any]]] = None,
    certificates: typing.Optional[typing.Sequence[typing.Union[EntrypointCertificateProps, typing.Dict[builtins.str, typing.Any]]]] = None,
    entrypoint_name: typing.Optional[builtins.str] = None,
    entrypoint_security_group_name: typing.Optional[builtins.str] = None,
    hosted_zone_props: typing.Optional[typing.Union[_aws_cdk_aws_route53_ceddda9d.HostedZoneAttributes, typing.Dict[builtins.str, typing.Any]]] = None,
    logs_bucket: typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket] = None,
    priority_allocator: typing.Optional[typing.Union[ApplicationListenerPriorityAllocatorConfig, typing.Dict[builtins.str, typing.Any]]] = None,
    security_group_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b43eb05048147e42be7ce96ae5872d2446ab14c342edc5bf6f712875dd6483e2(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    listener_arn: builtins.str,
    load_balancer_arn: builtins.str,
    security_group_id: builtins.str,
    domain_name: typing.Optional[builtins.str] = None,
    entrypoint_name: typing.Optional[builtins.str] = None,
    priority_allocator_service_token: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c307e05e08316e6716948431c89526e1e1f7f44d5d4eab8fc84fb48adcbf29ab(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    entrypoint_name: builtins.str,
    domain_name: typing.Optional[builtins.str] = None,
    vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
    vpc_lookup: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.VpcLookupOptions, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__445a7303c95b2fbb5bb62936f599717a2ce079e4765066c8938348b92a8c9d92(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    action: typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ListenerAction] = None,
    conditions: typing.Optional[typing.Sequence[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ListenerCondition]] = None,
    priority: typing.Optional[jsii.Number] = None,
    target_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.IApplicationTargetGroup]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c3fa4b14f324947bf3a512c16e6bae2a98a5d57e38faa72de2acedbcb6f1b8a3(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c1084d95fded1a099bfe9f522a419270d5befb1d6ad7a10234ddbb6933306b62(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    monitoring: typing.Optional[typing.Union[MonitoringFacadeProps, typing.Dict[builtins.str, typing.Any]]] = None,
    domain_name: builtins.str,
    networking: INetworking,
    certificate: typing.Optional[typing.Union[EntrypointCertificateProps, typing.Dict[builtins.str, typing.Any]]] = None,
    certificates: typing.Optional[typing.Sequence[typing.Union[EntrypointCertificateProps, typing.Dict[builtins.str, typing.Any]]]] = None,
    entrypoint_name: typing.Optional[builtins.str] = None,
    entrypoint_security_group_name: typing.Optional[builtins.str] = None,
    hosted_zone_props: typing.Optional[typing.Union[_aws_cdk_aws_route53_ceddda9d.HostedZoneAttributes, typing.Dict[builtins.str, typing.Any]]] = None,
    logs_bucket: typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket] = None,
    priority_allocator: typing.Optional[typing.Union[ApplicationListenerPriorityAllocatorConfig, typing.Dict[builtins.str, typing.Any]]] = None,
    security_group_name: typing.Optional[builtins.str] = None,
    analytics_reporting: typing.Optional[builtins.bool] = None,
    cross_region_references: typing.Optional[builtins.bool] = None,
    description: typing.Optional[builtins.str] = None,
    env: typing.Optional[typing.Union[_aws_cdk_ceddda9d.Environment, typing.Dict[builtins.str, typing.Any]]] = None,
    permissions_boundary: typing.Optional[_aws_cdk_ceddda9d.PermissionsBoundary] = None,
    stack_name: typing.Optional[builtins.str] = None,
    suppress_template_indentation: typing.Optional[builtins.bool] = None,
    synthesizer: typing.Optional[_aws_cdk_ceddda9d.IStackSynthesizer] = None,
    tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    termination_protection: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__42ae1e572e15914baf61e548ff4b4cb0bdcc9a6342df5a95deea60cb68f5ae80(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    action: typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ListenerAction] = None,
    conditions: typing.Optional[typing.Sequence[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ListenerCondition]] = None,
    priority: typing.Optional[jsii.Number] = None,
    target_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.IApplicationTargetGroup]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__180959596e187a102b6b1b0bf499744d61f500a85e4482b590b3d8c42be2feb3(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass
