import click
import importlib
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ..formats.neutral_format import NeutralFormat

FORMATS = ['coco', 'pascal_voc', 'yolo', 'createml', 'tensorflow_csv', 'labelme', 'vgg']

@click.command()
@click.option('--input-format', '-if', 
                required=True, 
                type=click.Choice(FORMATS, case_sensitive=False),
                callback=lambda ctx, param, value: value.lower(),
                help='Input dataset format')
@click.option('--input-path', '-ip', 
                required=True, 
                type=click.Path(exists=True), 
                help='Path to the Input dataset')
@click.option('--output-format', '-of', 
                required=True, 
                type=click.Choice(FORMATS, case_sensitive=False),
                callback=lambda ctx, param, value: value.lower(),
                help='Output dataset format')
@click.option('--output-path', '-op', 
                required=True, 
                type=click.Path(), 
                help='Path to save the Output dataset')
@click.option('--copy-images', is_flag=True, default=False, help='If set, copies image files to the output directory.')
@click.option('--symlink-images', is_flag=True, default=False, help='If set, creates symbolic links to the original images in the output directory.')
def vconverter(input_format, input_path, output_format, output_path, copy_images, symlink_images):
    """Convert object detection datasets between popular annotation formats.

    This CLI tool provides conversion between annotation formats through a neutral intermediate representation.

    \b
    Conversion Process:
        1. Reads input format and converts to neutral internal representation
        2. Transforms neutral format to target output format
        3. Saves converted format in output path

    \b
    Supported Formats:
        • COCO (JSON format with COCO dataset structure)
        • YOLO (TXT files with normalized coordinates)
        • Pascal VOC (XML files with Pascal VOC metadata)
        • CreateML (JSON file with list of annotations per image)
        • Tensorflow Object Detection CSV (single CSV file with annotations)
        • LabelMe JSON (JSON file for each image)
        • VGG Image Annotator JSON (single JSON file with annotation)
    """

    # Check if it has permissions to write
    if not os.access(os.path.dirname(output_path), os.W_OK):
        raise click.ClickException("Output path is not writable")

    try:
        # Dynamic import of format classes
        input_format_module = importlib.import_module(f'vision_converter.formats.{input_format}')
        input_format_class_name = f"{get_dataset_names(input_format)}Format"
        input_format_class = getattr(input_format_module, input_format_class_name)

        output_format_module = importlib.import_module(f'vision_converter.formats.{output_format}')
        output_format_class_name = f"{get_dataset_names(output_format)}Format"
        output_format_class = getattr(output_format_module, output_format_class_name)
        
        # Dynamic import of converters
        input_converter_module = importlib.import_module(f'vision_converter.converters.{input_format}_converter')
        input_converter_class_name = f"{get_dataset_names(input_format)}Converter"
        input_converter_class = getattr(input_converter_module,input_converter_class_name)

        output_converter_module = importlib.import_module(f'vision_converter.converters.{output_format}_converter')
        output_converter_class_name = f"{get_dataset_names(output_format)}Converter"
        output_converter_class = getattr(output_converter_module, output_converter_class_name)
        
        # Load input dataset
        message_read = f"Loading dataset {input_format} from {input_path} "
        if copy_images or symlink_images:
            message_read += f"with mode {'copy_images' if copy_images else 'symlink_images'}"

        click.echo(message_read)
        input_dataset = input_format_class.read_from_folder(input_path, copy_images, symlink_images)
        
        # Convert to NeutralFormat
        click.echo(f"Converting from {input_format} to neutral format...")
        neutral_format = input_converter_class.toNeutral(input_dataset)
        
        # Convert to output format
        click.echo(f"Converting from neutral format to {output_format}...")
        output_dataset = output_converter_class.fromNeutral(neutral_format)
        
        # Save output dataset 
        message_save = f"Saving dataset {output_format} in {output_path} "
        if copy_images or symlink_images:
            message_save += f"with mode {'copy_images' if copy_images else 'symlink_images'}"

        click.echo(message_save)
        output_dataset.save(output_path, copy_images, symlink_images)
        
    except ImportError as e:
        click.echo(f"Error: Could not import necessary modules: {e}", err=True)
        sys.exit(1)
    except AttributeError as e:
        click.echo(f"Error: Lacking class or required method: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Error while converting: {e}", err=True)
        sys.exit(1)

def get_dataset_names(input: str) -> str:
    # Map special cases
    specific_formats = {
        'createml': 'CreateML',
        'labelme': 'LabelMe',
        'vgg': 'VGG'
    }
    
    # For special cases
    if input.lower() in specific_formats:
        return specific_formats[input.lower()]
    
    # default
    return "".join(word.capitalize() for word in input.split("_"))


if __name__ == "__main__":
    vconverter()
