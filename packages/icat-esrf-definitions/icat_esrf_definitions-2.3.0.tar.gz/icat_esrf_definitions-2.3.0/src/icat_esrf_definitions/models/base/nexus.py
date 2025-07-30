"""Base models to represent ICAT schema's associated to NeXus NXDL instances."""

from typing import Literal

from pydantic import Field

from .model import IcatBaseModel


class NXobject(IcatBaseModel):
    NX_class: str = Field(..., alias="@NX_class")


class NXentry(NXobject):
    NX_class: Literal["NXentry"] = Field("NXentry", alias="@NX_class")


class NXsubentry(NXobject):
    NX_class: Literal["NXsubentry"] = Field("NXsubentry", alias="@NX_class")


class NXnote(NXobject):
    NX_class: Literal["NXnote"] = Field("NXnote", alias="@NX_class")


class NXcollection(NXobject):
    NX_class: Literal["NXcollection"] = Field("NXcollection", alias="@NX_class")


class NXpositioner(NXobject):
    NX_class: Literal["NXpositioner"] = Field("NXpositioner", alias="@NX_class")


class NXdetector(NXobject):
    NX_class: Literal["NXdetector"] = Field("NXdetector", alias="@NX_class")


class NXsample(NXobject):
    NX_class: Literal["NXsample"] = Field("NXsample", alias="@NX_class")


class NXprocess(NXobject):
    NX_class: Literal["NXprocess"] = Field("NXprocess", alias="@NX_class")


class NXcite(NXobject):
    NX_class: Literal["NXcite"] = Field("NXcite", alias="@NX_class")


class NXenvironment(NXobject):
    NX_class: Literal["NXenvironment"] = Field("NXenvironment", alias="@NX_class")


class NXfresnel_zone_plate(NXobject):
    NX_class: Literal["NXfresnel_zone_plate"] = Field(
        "NXfresnel_zone_plate", alias="@NX_class"
    )


class NXgeometry(NXobject):
    NX_class: Literal["NXgeometry"] = Field("NXgeometry", alias="@NX_class")


class NXmirror(NXobject):
    NX_class: Literal["NXmirror"] = Field("NXmirror", alias="@NX_class")


class NXinstrument(NXobject):
    NX_class: Literal["NXinstrument"] = Field("NXinstrument", alias="@NX_class")


class NXbeam(NXobject):
    NX_class: Literal["NXbeam"] = Field("NXbeam", alias="@NX_class")


class NXmonochromator(NXobject):
    NX_class: Literal["NXmonochromator"] = Field("NXmonochromator", alias="@NX_class")


class NXcrystal(NXobject):
    NX_class: Literal["NXcrystal"] = Field("NXcrystal", alias="@NX_class")


class NXsource(NXobject):
    NX_class: Literal["NXsource"] = Field("NXsource", alias="@NX_class")


class NXslit(NXobject):
    NX_class: Literal["NXslit"] = Field("NXslit", alias="@NX_class")


class NXxraylens(NXobject):
    NX_class: Literal["NXxraylens"] = Field("NXxraylens", alias="@NX_class")


class NXattenuator(NXobject):
    NX_class: Literal["NXattenuator"] = Field("NXattenuator", alias="@NX_class")


class NXsensor(NXobject):
    NX_class: Literal["NXsensor"] = Field("NXsensor", alias="@NX_class")


class NXaperture(NXobject):
    NX_class: Literal["NXaperture"] = Field("NXaperture", alias="@NX_class")


class NXinsertion_device(NXobject):
    NX_class: Literal["NXinsertion_device"] = Field(
        "NXinsertion_device", alias="@NX_class"
    )
