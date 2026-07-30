import os
import pytest
import importlib
from helpers.utils import read_data

script = importlib.import_module("aci-preupgrade-validation-script")
dir = os.path.dirname(os.path.abspath(__file__))

test_function = "routeep_msite_pbr_host_prefix_check"

msite_query = "fvFabricExtConnP.json?rsp-subtree=children"
graph_query = (
    'vnsGraphInst.json?query-target-filter=eq(vnsGraphInst.configSt,"applied")'
    '&rsp-subtree=children&rsp-subtree-class=vnsNodeInst&rsp-subtree-include=required'
)
stretched_vrf_query = "fvCtx.json?rsp-subtree=children&rsp-subtree-class=fvSiteAssociated&rsp-subtree-include=required"
vzany_query = "fvCtx.json?rsp-subtree=full&rsp-subtree-class=vzRsAnyToCons,vzRsAnyToProv"
epg_query = (
    "fvAEPg.json?rsp-subtree=full&rsp-subtree-class="
    "fvSubnet,fvEpAnycast,fvEpNlb,fvEpReachability&rsp-subtree-include=required"
)
fault_query = 'faultInst.json?query-target-filter=eq(faultInst.code,"F4692")'


@pytest.mark.parametrize(
    "icurl_outputs, cversion, tversion, expected_result",
    [
        ({}, None, None, script.MANUAL),
        (
            {
                fault_query: [],
                msite_query: read_data(dir, "fvFabricExtConnP_no_msite.json"),
            },
            "6.1(4h)",
            "6.1(4h)",
            script.PASS,
        ),
        (
            {
                fault_query: read_data(dir, "faultInst_F4692_raised.json"),
                msite_query: read_data(dir, "fvFabricExtConnP_no_msite.json"),
            },
            "6.1(4h)",
            "6.1(4h)",
            script.PASS,
        ),
        (
            {
                fault_query: read_data(dir, "faultInst_F4692_raised.json"),
                msite_query: read_data(dir, "fvFabricExtConnP_no_msite.json"),
            },
            "6.1(3g)",
            "6.1(4h)",
            script.PASS,
        ),
        (
            {
                fault_query: read_data(dir, "faultInst_F4692_cleared.json"),
                msite_query: read_data(dir, "fvFabricExtConnP_no_msite.json"),
            },
            "6.2(2e)",
            "6.1(4h)",
            script.PASS,
        ),
        (
            {
                fault_query: read_data(dir, "faultInst_F4692_raised.json"),
                msite_query: read_data(dir, "fvFabricExtConnP_with_msite.json"),
                graph_query: read_data(dir, "vnsGraphInst_redirect_c1.json"),
                stretched_vrf_query: read_data(dir, "fvCtx_stretched_vrf1.json"),
                vzany_query: read_data(dir, "fvCtx_vzany_to_cons_c1.json"),
                epg_query: read_data(dir, "fvAEPg_hostprefix_32_with_anycast_dpdisabled.json"),
            },
            "6.2(2e)",
            "6.1(4h)",
            script.FAIL_O,
        ),
        (
            {
                fault_query: read_data(dir, "faultInst_F4692_raised.json"),
                msite_query: read_data(dir, "fvFabricExtConnP_no_msite.json"),
            },
            "6.2(2e)",
            "6.1(3g)",
            script.PASS,
        ),
        (
            {
                msite_query: read_data(dir, "fvFabricExtConnP_no_msite.json"),
            },
            "6.1(3g)",
            "6.1(3g)",
            script.PASS,
        ),
        (
            {
                msite_query: read_data(dir, "fvFabricExtConnP_with_msite.json"),
                graph_query: read_data(dir, "vnsGraphInst_redirect_c1.json"),
                stretched_vrf_query: read_data(dir, "fvCtx_stretched_vrf1.json"),
                vzany_query: read_data(dir, "fvCtx_vzany_to_cons_c1.json"),
                epg_query: read_data(dir, "fvAEPg_hostprefix_32_with_anycast_dpdisabled.json"),
            },
            "6.1(3g)",
            "6.1(3g)",
            script.FAIL_O,
        ),
        (
            {
                msite_query: read_data(dir, "fvFabricExtConnP_with_msite.json"),
                graph_query: read_data(dir, "vnsGraphInst_redirect_c1.json"),
                stretched_vrf_query: read_data(dir, "fvCtx_stretched_vrf1.json"),
                vzany_query: read_data(dir, "fvCtx_vzany_to_prov_c1.json"),
                epg_query: read_data(dir, "fvAEPg_non_hostprefix_24_with_anycast_dpdisabled.json"),
            },
            "6.1(3g)",
            "6.1(3g)",
            script.PASS,
        ),
    ],
)
def test_logic(run_check, mock_icurl, cversion, tversion, expected_result):
    result = run_check(
        cversion=script.AciVersion(cversion) if cversion else None,
        tversion=script.AciVersion(tversion) if tversion else None,
    )
    assert result.result == expected_result
