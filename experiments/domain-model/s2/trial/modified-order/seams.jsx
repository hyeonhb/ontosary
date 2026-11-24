// Presentation and provider seams for the four pinned controls. The real Input,
// dialog, selection hook and quantity/payment utilities come from each copy.
import React from 'react';
const childrenOnly = ({ children }) => children;
export const Trans = childrenOnly;
export const Label = childrenOnly, DialogContent = childrenOnly, DialogTitle = childrenOnly,
    DialogDescription = childrenOnly, DialogHeader = childrenOnly, DialogFooter = childrenOnly;
export const Dialog = ({ open, children }) => open ? <section role="dialog">{children}</section> : null;
export const Alert = childrenOnly, AlertDescription = childrenOnly, Button = childrenOnly;
export const Select = childrenOnly, SelectContent = childrenOnly, SelectItem = childrenOnly,
    SelectTrigger = childrenOnly, SelectValue = () => null;
export const Checkbox = () => null, VendureImage = () => null, AlertCircle = () => null;
export const cn = (...classes) => classes.join(' ');
export const useLingui = () => ({ t: String.raw });
export const useDynamicTranslations = () => ({ getTranslatedRefundReason: String });
export const useLocalFormat = () => ({ formatCurrency: String, toMajorUnits: n => n/100, toMinorUnits: n => n*100 });
export const uiConfig = { orders: { refundReasons: [] } };
export const DEFAULT_CHANNEL_CODE = '__default_channel__';
export const cancelOrderDocument = 'cancel', refundOrderDocument = 'refund';
const noSubmission = () => { throw Error('Quantity probe does not submit mutations'); };
export const api = { mutate: () => noSubmission };
export const useMutation = () => ({ mutateAsync: noSubmission });
export const toast = { error: noSubmission, success: noSubmission, warning: noSubmission };
