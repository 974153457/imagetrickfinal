from flask import render_template, redirect, url_for, request
from app import webapp

import boto3
from app import config
from datetime import datetime, timedelta
from operator import itemgetter




@webapp.route('/ec2_examples', methods=['POST'])
# Create a new student and save them in the database.
def parameters():
    code = request.form.get('code', "")
    title = request.form.get('title', "")
    description = request.form.get('description', "")


    error = False

    if code == "" or title == "" or description == "":
        error = True
        error_msg = "Error: All fields are required!"

    if error:
        return render_template("ec2_examples/list.html", title="New Course", error_msg=error_msg,  ctitle=title,
                               description=description)

    print(code)
    print(title)
    print(description)



########################################## 列出正在运行的cpu的利用率
    allrunningid_cpu = []

    ec2 = boto3.resource('ec2')  # 检差正在running的实例
    instances = ec2.instances.filter(
        Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])
    for instance in instances:
        allrunningid_cpu.append(instance.id)  # instance id save in list

    totalrunnumber_cpu = len(allrunningid_cpu)  # num of running instance


    xixi = 1
    haha = 0

    cpu_utilizationlist = []

    while xixi <= totalrunnumber_cpu:
        ec2 = boto3.resource('ec2')
        instance = ec2.Instance(allrunningid_cpu[haha])
        # instances = ec2.instances.all()
        client = boto3.client('cloudwatch')

        metric_name = 'CPUUtilization'
        namespace = 'AWS/EC2'
        statistic = 'Average'  # could be Sum,Maximum,Minimum,SampleCount,Average

        cpu = client.get_metric_statistics(
            Period=1 * 60,
            StartTime=datetime.utcnow() - timedelta(seconds=60 * 60),
            EndTime=datetime.utcnow() - timedelta(seconds=0 * 60),
            MetricName=metric_name,
            Namespace=namespace,  # Unit='Percent',
            Statistics=[statistic],
            Dimensions=[{'Name': 'InstanceId', 'Value': allrunningid_cpu[haha]}]
        )

        cpu_stats = []

        for point in cpu['Datapoints']:
            hour = point['Timestamp'].hour
            minute = point['Timestamp'].minute
            time = hour + minute / 60
            cpu_stats.append([time, point['Average']])

        cpu_stats = sorted(cpu_stats, key=itemgetter(0))

        aaa = cpu_stats[-1]
        bbb = aaa[1]
        print(bbb)
        cpu_utilizationlist.append(bbb)

        xixi = xixi+1
        haha = haha+1

    print(cpu_utilizationlist)


############################################################   给定个数创建instance



    allrunningid = []

    ec2 = boto3.resource('ec2')               #检差正在running的实例
    instances = ec2.instances.filter(
        Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])
    for instance in instances:
        print(instance.id)
        allrunningid.append(instance.id)      #instance id save in list

    print(allrunningid)

    totalrunnumber = len(allrunningid)   #num of running instance

    print(totalrunnumber)

#    needrunnumber = totalrunnumber * 2 -totalrunnumber
############################################################   给定个数创建instance
    needrunnumber = 3    ######################    成倍数增加instance


    i=10000000
    while i <= needrunnumber:

        ec2 = boto3.resource('ec2')
        client = boto3.client('elb')

        xindeinstance = ec2.create_instances(ImageId=config.ami_id,
                                             MinCount=1,
                                             MaxCount=1,
                                             KeyName='ece1779winter_as1',
                                             InstanceType='t2.small',
                                             SubnetId='subnet-f52970ae',
                                             Monitoring={'Enabled': True},
                                             SecurityGroupIds=['sg-85565cf9']
                                             )
        for x in xindeinstance:
            xindeID = x.id
            print(xindeID)

        response = client.register_instances_with_load_balancer(
            Instances=[
                {
                    'InstanceId': xindeID,
                },
            ],
            LoadBalancerName='loadbalancertest',
        )

        xindeinstance = None
        response = None
        ec2 = None
        client = None
        i = i+1

    print ("creat three new instance")


##############################################################     reduce instance
    ruducerate = 2

    allrunningid2 = []

    ec2 = boto3.resource('ec2')  # 检差正在running的实例
    instances = ec2.instances.filter(
        Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])
    for instance in instances:
        print(instance.id)
        allrunningid2.append(instance.id)  # instance id save in list

    print(allrunningid2)

    totalrunnumber = len(allrunningid)  # num of running instance

    print(totalrunnumber)

    if 'i-090172e1cafb9ca2d' in allrunningid2:
        allrunningid2.remove('i-090172e1cafb9ca2d')

    print(allrunningid2)


    needreducenumber = 2

    ii = 10000000
    a = totalrunnumber -2
    while ii <= needreducenumber :
        ec2 = boto3.resource('ec2')

        ec2.instances.filter(InstanceIds=[allrunningid2[a]]).terminate()

        ii = ii +1
        a = a - 1


    return redirect(url_for('ec2_list'))




@webapp.route('/ec2_examples',methods=['GET'])
# Display an HTML list of all ec2 instances
def ec2_list():

    # create connection to ec2
    ec2 = boto3.resource('ec2')

#    instances = ec2.instances.filter(
#        Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])

    instances = ec2.instances.all()

#    for x in instances:
#        print(x.id)

    return render_template("ec2_examples/list.html",title="EC2 Instances",instances=instances)


@webapp.route('/ec2_examples/displayallcpu',methods=['POST'])
def displaycpu():
    ec2 = boto3.resource('ec2')
    id = 'i-005ed98a4a89dc0d6'
    instance = ec2.Instance(id)
    #instances = ec2.instances.all()
    client = boto3.client('cloudwatch')

    metric_name = 'CPUUtilization'
    namespace = 'AWS/EC2'
    statistic = 'Average'  # could be Sum,Maximum,Minimum,SampleCount,Average

    cpu = client.get_metric_statistics(
        Period=1 * 60,
        StartTime=datetime.utcnow() - timedelta(seconds=60 * 60),
        EndTime=datetime.utcnow() - timedelta(seconds=0 * 60),
        MetricName=metric_name,
        Namespace=namespace,  # Unit='Percent',
        Statistics=[statistic],
        Dimensions=[{'Name': 'InstanceId', 'Value': id}]
    )

    cpu_stats = []

    for point in cpu['Datapoints']:
        hour = point['Timestamp'].hour
        minute = point['Timestamp'].minute
        time = hour + minute / 60
        cpu_stats.append([time, point['Average']])

    cpu_stats = sorted(cpu_stats, key=itemgetter(0))

    aaa = cpu_stats[-1]
    bbb = aaa[1]
    print(bbb)



    return render_template("ec2_examples/displayallCpu.html",title = "All CPU Utilization",
                           instance=instance,
                           cpu_stats=cpu_stats)






@webapp.route('/ec2_examples/<id>',methods=['GET'])
#Display details about a specific instance.
def ec2_view(id):
    ec2 = boto3.resource('ec2')

    instance = ec2.Instance(id)

    client = boto3.client('cloudwatch')

    metric_name = 'CPUUtilization'

    ##    CPUUtilization, NetworkIn, NetworkOut, NetworkPacketsIn,
    #    NetworkPacketsOut, DiskWriteBytes, DiskReadBytes, DiskWriteOps,
    #    DiskReadOps, CPUCreditBalance, CPUCreditUsage, StatusCheckFailed,
    #    StatusCheckFailed_Instance, StatusCheckFailed_System


    namespace = 'AWS/EC2'
    statistic = 'Average'                   # could be Sum,Maximum,Minimum,SampleCount,Average



    cpu = client.get_metric_statistics(
        Period=1 * 60,
        StartTime=datetime.utcnow() - timedelta(seconds=60 * 60),
        EndTime=datetime.utcnow() - timedelta(seconds=0 * 60),
        MetricName=metric_name,
        Namespace=namespace,  # Unit='Percent',
        Statistics=[statistic],
        Dimensions=[{'Name': 'InstanceId', 'Value': id}]
    )

    cpu_stats = []


    for point in cpu['Datapoints']:
        hour = point['Timestamp'].hour
        minute = point['Timestamp'].minute
        time = hour + minute/60
        cpu_stats.append([time,point['Average']])

    cpu_stats = sorted(cpu_stats, key=itemgetter(0))


    statistic = 'Sum'  # could be Sum,Maximum,Minimum,SampleCount,Average

    network_in = client.get_metric_statistics(
        Period=1 * 60,
        StartTime=datetime.utcnow() - timedelta(seconds=60 * 60),
        EndTime=datetime.utcnow() - timedelta(seconds=0 * 60),
        MetricName='NetworkIn',
        Namespace=namespace,  # Unit='Percent',
        Statistics=[statistic],
        Dimensions=[{'Name': 'InstanceId', 'Value': id}]
    )

    net_in_stats = []

    for point in network_in['Datapoints']:
        hour = point['Timestamp'].hour
        minute = point['Timestamp'].minute
        time = hour + minute/60
        net_in_stats.append([time,point['Sum']])

    net_in_stats = sorted(net_in_stats, key=itemgetter(0))



    network_out = client.get_metric_statistics(
        Period=5 * 60,
        StartTime=datetime.utcnow() - timedelta(seconds=60 * 60),
        EndTime=datetime.utcnow() - timedelta(seconds=0 * 60),
        MetricName='NetworkOut',
        Namespace=namespace,  # Unit='Percent',
        Statistics=[statistic],
        Dimensions=[{'Name': 'InstanceId', 'Value': id}]
    )


    net_out_stats = []

    for point in network_out['Datapoints']:
        hour = point['Timestamp'].hour
        minute = point['Timestamp'].minute
        time = hour + minute/60
        net_out_stats.append([time,point['Sum']])

        net_out_stats = sorted(net_out_stats, key=itemgetter(0))


    return render_template("ec2_examples/view.html",title="Instance Info",
                           instance=instance,
                           cpu_stats=cpu_stats,
                           net_in_stats=net_in_stats,
                           net_out_stats=net_out_stats)


@webapp.route('/ec2_examples/create',methods=['POST'])
# Start a new EC2 instance
def ec2_create():

    ec2 = boto3.resource('ec2')
    client = boto3.client('elb')

    xindeinstance = ec2.create_instances(ImageId=config.ami_id,
                         MinCount=1,
                         MaxCount=1,
                         KeyName='ece1779winter_as1',
                         InstanceType='t2.small',
                         SubnetId='subnet-f52970ae',
                         Monitoring = {'Enabled':True},
                         SecurityGroupIds=['sg-85565cf9']
                         )
    for x in xindeinstance:
        xindeID = x.id
        print(xindeID)

    response = client.register_instances_with_load_balancer(
        Instances=[
            {
                'InstanceId': xindeID ,
            },
        ],
        LoadBalancerName='loadbalancertest',
    )
    print(response)


    """
    xindeinstance = None
    response = None
    ec2 = None
    client = None
    ec2 = boto3.resource('ec2')
    client = boto3.client('elb')

    xindeinstance = ec2.create_instances(ImageId=config.ami_id,
                                         MinCount=1,
                                         MaxCount=1,
                                         KeyName='ece1779winter_as1',
                                         InstanceType='t2.small',
                                         SubnetId='subnet-f52970ae',
                                         Monitoring={'Enabled': True},
                                         SecurityGroupIds=['sg-85565cf9']
                                         )
    for x in xindeinstance:
        xindeID = x.id
        print(xindeID)

    response = client.register_instances_with_load_balancer(
        Instances=[
            {
                'InstanceId': xindeID,
            },
        ],
        LoadBalancerName='loadbalancertest',
    )
    print(response)
    """

    return redirect(url_for('ec2_list'))



@webapp.route('/ec2_examples/delete/<id>',methods=['POST'])
# Terminate a EC2 instance
def ec2_destroy(id):
    # create connection to ec2
    ec2 = boto3.resource('ec2')

    ec2.instances.filter(InstanceIds=[id]).terminate()

    return redirect(url_for('ec2_list'))




"""@webapp.route('/ec2_examples/managerlogin',methods=['GET'])
# Display an empty HTML form that allows users to define new student.
def managerlogin():
    return render_template("ec2_examples/managerlogin.html",title="Manager Login")


@webapp.route('/ec2_examples/managerlogin', methods=['POST'])
# Create a new student and save them in the database.
def managerlogin_save():


    a = request.form.get('login', "")
    title = request.form.get('passwords', "")

    error = False

    if a == "" or title == "" :
        error = True
        error_msg = "Error: All fields are required!"

    if error:
        return render_template("ec2_examples/managerlogin.html", title="Manager Login", error_msg=error_msg, login=a, passwords=title)

    if a == 'admin':
        return redirect(url_for('ec2_list'))
    else:
        error_msg = "Error:Wrong Manager User Name"
        return render_template("ec2_examples/managerlogin.html", title="Manager Login", error_msg=error_msg, login=a,
                               passwords=title)


    """




