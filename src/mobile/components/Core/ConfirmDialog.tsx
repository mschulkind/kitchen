/**
 * ConfirmDialog Component 🗑️
 * 
 * Custom confirmation dialog replacing browser's window.confirm().
 * Works consistently across web and native platforms.
 */

import { AlertDialog, Button, XStack, YStack, Paragraph, H2 } from 'tamagui';

interface ConfirmDialogProps {
  open: boolean;
  onConfirm: () => void;
  onCancel: () => void;
  title: string;
  message: string;
  confirmText?: string;
  cancelText?: string;
  destructive?: boolean;
}

export function ConfirmDialog({
  open,
  onConfirm,
  onCancel,
  title,
  message,
  confirmText = 'Delete',
  cancelText = 'Cancel',
  destructive = true,
}: ConfirmDialogProps) {
  return (
    <AlertDialog open={open} onOpenChange={(isOpen) => !isOpen && onCancel()}>
      <AlertDialog.Portal>
        <AlertDialog.Overlay
          key="overlay"
          animation="quick"
          opacity={0.5}
          enterStyle={{ opacity: 0 }}
          exitStyle={{ opacity: 0 }}
        />
        <AlertDialog.Content
          bordered
          elevate
          key="content"
          animation={['quick', { opacity: { overshootClamping: true } }]}
          enterStyle={{ x: 0, y: -20, opacity: 0, scale: 0.9 }}
          exitStyle={{ x: 0, y: 10, opacity: 0, scale: 0.95 }}
          x={0}
          scale={1}
          opacity={1}
          y={0}
          maxWidth={400}
          width="90%"
        >
          <YStack space="$3" padding="$4">
            <AlertDialog.Title>
              <H2 size="$5">{title}</H2>
            </AlertDialog.Title>
            <AlertDialog.Description>
              <Paragraph size="$3" color="$gray11">{message}</Paragraph>
            </AlertDialog.Description>

            <XStack space="$3" justifyContent="flex-end" marginTop="$2">
              <AlertDialog.Cancel asChild>
                <Button chromeless onPress={onCancel}>{cancelText}</Button>
              </AlertDialog.Cancel>
              <AlertDialog.Action asChild>
                <Button
                  theme={destructive ? 'red' : 'blue'}
                  onPress={onConfirm}
                >
                  {confirmText}
                </Button>
              </AlertDialog.Action>
            </XStack>
          </YStack>
        </AlertDialog.Content>
      </AlertDialog.Portal>
    </AlertDialog>
  );
}
