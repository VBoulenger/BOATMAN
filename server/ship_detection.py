"""
Extract ship coordinates from SENTINEL-1 data files
"""
from pathlib import Path

from snapista import Graph
from snapista import Operator


def add_read_node(graph_l: Graph, input_filename: Path):
    graph_l.add_node(
        operator=Operator(
            "Read",
            formatName="SENTINEL-1",
            file=str(input_filename),
            copyMetadata="true",
        ),
        node_id="read",
    )


def add_write_node(graph_l: Graph, output_filename: Path):
    if output_filename.suffix != ".dim":
        raise NameError(
            f"The output file has to be '.dim', but is currently: \"{output_filename}\""
        )

    graph_l.add_node(
        operator=Operator("Write", formatName="BEAM-DIMAP", file=str(output_filename)),
        node_id="write",
        source="object_discrimination",
    )


def add_land_sea_mask(graph_l: Graph):
    graph_l.add_node(
        operator=Operator(
            "Land-Sea-Mask",
            landMask="true",
            useSRTM="true",
            invertGeometry="false",
            shorelineExtension="20",
        ),
        node_id="land_sea_mask",
        source="read",
    )


def add_calibration(graph_l: Graph):
    graph_l.add_node(
        operator=Operator(
            "Calibration",
            auxFile="Product Auxiliary File",
            outputImageInComplex="false",
            outputImageScaleInDb="false",
            createGammaBand="false",
            createBetaBand="false",
            outputSigmaBand="true",
            outputGammaBand="false",
            outputBetaBand="false",
        ),
        node_id="calibration",
        source="land_sea_mask",
    )


def add_adaptive_thresholding(graph_l: Graph):
    graph_l.add_node(
        operator=Operator(
            "AdaptiveThresholding",
            targetWindowSizeInMeter="50",
            guardWindowSizeInMeter="500.0",
            backgroundWindowSizeInMeter="800.0",
            pfa="12.5",
            estimateBackground="false",
        ),
        node_id="adaptive_thresholding",
        source="calibration",
    )


def add_object_discrimination(graph_l: Graph):
    graph_l.add_node(
        operator=Operator(
            "Object-Discrimination",
            minTargetSizeInMeter="30.0",
            maxTargetSizeInMeter="600.0",
        ),
        node_id="object_discrimination",
        source="adaptive_thresholding",
    )


def add_preprocessing(graph_l: Graph):
    add_land_sea_mask(graph_l)
    add_calibration(graph_l)
    add_adaptive_thresholding(graph_l)
    add_object_discrimination(graph_l)


def process(filename: Path):
    if not filename.exists():
        raise FileNotFoundError(filename)

    output_path = filename.with_suffix(".dim")

    if output_path.exists():
        print("Result already exists, skipping")
        return

    graph = Graph()

    add_read_node(graph, filename)
    add_preprocessing(graph)
    add_write_node(graph, output_path)

    graph.run()


if __name__ == "__main__":
    # Set Path to Input Satellite Data
    input_path = Path(
        "../Data/Singapour/S1A_IW_GRDH_1SDV_20221012T224816_20221012T224841_045415_056E4B_7DC8.zip"
    )

    process(input_path)
