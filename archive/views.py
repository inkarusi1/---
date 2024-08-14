from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.urls import reverse
from .models import BlockInfo, CodeHierarchy
from django.template import loader
from django.views import generic
import pandas as pd


missing_children = set()


class IndexView(generic.ListView):
    template_name = "archive/index.html"
    context_object_name = "latest_block_list"

    def get_queryset(self):
        """Return the last five published blocks."""
        return BlockInfo.objects.order_by("-block_id")[:5]


class DetailView(generic.DetailView):
    model = BlockInfo
    template_name = "archive/detail.html"


class ResultsView(generic.DetailView):
    model = BlockInfo
    template_name = "archive/results.html"


def index(request):
    latest_block_list = BlockInfo.objects.order_by("-block_id")[:]
    context = {
        "latest_block_list": latest_block_list,
    }
    output = ", ".join([b.block_name for b in latest_block_list])
    # return HttpResponse("Hello, world. You're at the polls index.\n" + output)
    return render(request, "archive/index.html", context)


def detail(request, block_id):
    # try:
    #     block = BlockInfo.objects.get(pk=block_id)
    # except BlockInfo.DoesNotExist:
    #     raise Http404("BlockInfo does not exist")
    block = get_object_or_404(BlockInfo, pk=block_id)

    return render(request, "archive/detail.html", {"block": block})


def results(request, block_id):
    response = "You're looking at the results of question %s."
    block = get_object_or_404(BlockInfo, pk=block_id)
    return render(request, "archive/results.html", {"block": block})


def modify_block(request, block_id):
    block = get_object_or_404(BlockInfo, pk=block_id)
    try:
        block.block_name = request.POST['block_name']
        block.block_name_zh = request.POST['block_name_zh']
        block.lang = request.POST['lang']
        block.block_function = request.POST['func']
        block.in_module = request.POST['module']
        block.code = request.POST['code']
    except (KeyError, AttributeError):
        return render(request, "archive/detail.html", {
            "block": block,
            "error_message": "key error!!!",
        })
    else:
        block.save()
        return HttpResponseRedirect(reverse("archive:results", args=(block.block_id,)))


def delete_block(request, block_id):
    block = get_object_or_404(BlockInfo, pk=block_id)
    block.delete()
    return HttpResponseRedirect(reverse("archive:index"))


def add_block_view(request):
    return render(request, "archive/add_block.html", {})


def add_block(request):
    global missing_children
    try:
        block = BlockInfo(block_name=request.POST['block_name'], block_name_zh=request.POST['block_name_zh'],
                          lang=request.POST['lang'], block_function=request.POST['func'],
                          in_module=request.POST['module'], code=request.POST['code'])
        name_list = request.POST['children'].split(',')
        name_list = [name.strip()[1:-1] for name in name_list]
        block_list = []
        for name in name_list:
            if BlockInfo.objects.filter(block_name=name).exists():
                block_list.append(BlockInfo.objects.get(block_name=name))
            else:
                missing_children.add(name)
        # block_list = [BlockInfo.objects.get(block_name=name) for name in name_list]
    except (KeyError, AttributeError, BlockInfo.DoesNotExist):
        return render(request, "archive/index.html", {})
    else:
        block.save()
        print(missing_children)
        for b in block_list:
            code_hierarchy = CodeHierarchy(block_id=b, superior_block_id=block, is_leaf=True)
            code_hierarchy.save()
        return HttpResponseRedirect(reverse("archive:index"))


def add_blocks_from_excel(request):
    if request.method == 'POST':
        excel_file = request.FILES.get("excel_file")
        if not excel_file:
            return HttpResponse("no file for upload")
        data = pd.read_excel(excel_file)
        id2block = {}
        # 保存代码块信息
        for i in range(len(data)):
            block = BlockInfo(block_name=data.loc[i, "代码块名称"], block_name_zh=data.loc[i, "代码块中文名称"],
                              lang=data.loc[i, "开发语言（生成代码语言）"], block_function=data.loc[i, "代码块作用"],
                              in_module=data.loc[i, "仿真系统引用功能"], code=data.loc[i, "代码文件"])
            id2block[int(data.loc[i, "代码块id"])] = block
            block_name = data.loc[i, "代码块名称"]
            # 检查是否已存在具有相同block_name的BlockInfo对象
            if BlockInfo.objects.filter(block_name=block_name).exists():
                # 如果存在，可以选择更新该对象，或者跳过插入新对象的步骤
                continue
            block.save()
        # 保存代码块层次信息
        non_leaf_set = set()
        hierarchy_list = []
        print(f'id2block: {id2block}')
        for i in range(len(data)):
            id_list = str(data.loc[i, "上级代码块id"]).split(',')
            id_list = [int(_id.strip()) for _id in id_list]
            print(f'id_list: {id_list}')
            non_leaf_set.update(id_list)
            for _id in id_list:
                if _id in id2block:
                    hierarchy_list.append((int(data.loc[i, "代码块id"]), _id))
                else:
                    print(f'block_id: {data.loc[i, "代码块id"]}, superior_block_id: {_id}')
        print(f'len of hierarchy_list: {len(hierarchy_list)}')
        for (block_id, superior_block_id) in hierarchy_list:
            print(f'block_id: {block_id}, superior_block_id: {superior_block_id}')
            if CodeHierarchy.objects.filter(block_id=id2block[block_id],
                                            superior_block_id=id2block[superior_block_id]).exists():
                continue
            code_hierarchy = CodeHierarchy(block_id=id2block[block_id], superior_block_id=id2block[superior_block_id],
                                           is_leaf=(block_id not in non_leaf_set))
            code_hierarchy.save()
        return HttpResponseRedirect(reverse("archive:index"))
    return HttpResponseRedirect(reverse("archive:index"))
