# -*- coding: utf-8 -*-
from datetime import datetime

from marshmallow import Schema, fields


class TimeLine(Schema):
    invoce_datetime = fields.DateTime()
    due_datetime = fields.DateTime()


if __name__ == "__main__":

    specific_moment = {
        "invoce_datetime": "2020-5-12 10:00:00",
        "due_datetime": datetime.utcnow().isoformat(),
    }

    load_sm = TimeLine(strict=True).load(specific_moment).data
    print(f"load_sm: {load_sm}")

    dump_sm = TimeLine(strict=True).dump(load_sm).data
    print(f"dump_sm: {dump_sm}")

