from flask import request, url_for


def get_page(default=1):
    try:
        return max(1, int(request.args.get("page", default)))
    except (TypeError, ValueError):
        return default


def get_per_page(default=25):
    try:
        per_page = int(request.args.get("per_page", default))
        return per_page if per_page in (25, 50, 100) else default
    except (TypeError, ValueError):
        return default


def pagination_context(pagination, endpoint, **kwargs):
    args = request.args.to_dict()
    args.pop("page", None)

    def page_url(page_num):
        args["page"] = page_num
        return url_for(endpoint, **kwargs, **args)

    return {
        "pagination": pagination,
        "page_url": page_url,
        "per_page": pagination.per_page,
    }
