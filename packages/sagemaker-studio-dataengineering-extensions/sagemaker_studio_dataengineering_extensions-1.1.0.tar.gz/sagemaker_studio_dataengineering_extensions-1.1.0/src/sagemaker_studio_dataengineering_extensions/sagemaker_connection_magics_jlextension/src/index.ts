import { connectionDropdownPlugin } from './ConnectionDropdownWidget';
import { codeMirrorPlugin } from './ConnectionMagicFormat';
import { libManagementPlugin } from './LibManagementEditor';
import { newCellMagicLineHandler } from './NewCellMagicLineHandler';
import { sqlQuerybookEditor } from './SqlQuerybookEditor';
import { visualEtlFileEditor } from './VisualEtlFileEditor';
import { debuggingPlugin } from "./DebuggingJLPlugin";
import { sagemakerDisplayMimeRender } from "./DataVisualizationRender";

export default [
  connectionDropdownPlugin,
  newCellMagicLineHandler,
  codeMirrorPlugin,
  libManagementPlugin,
  sqlQuerybookEditor,
  visualEtlFileEditor,
  debuggingPlugin,
  sagemakerDisplayMimeRender
];
