import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Switch,
  Alert,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { useRouter } from 'expo-router';
import { useLanguage } from '../src/context/LanguageContext';
import { useAuth } from '../src/context/AuthContext';
import { translations } from '../src/i18n/translations';

export default function NotificationSettingsScreen() {
  const router = useRouter();
  const { language } = useLanguage();
  const { user, updateNotificationPreferences } = useAuth();
  const t = translations[language];

  const prefs = user?.notificationPreferences || {
    payment_reminders: true,
    deposit_alerts: true,
    monthly_reports: true,
    push_enabled: true,
  };

  const handleToggle = async (key: string, value: boolean) => {
    const success = await updateNotificationPreferences({ [key]: value });
    if (!success) {
      Alert.alert(t.error, 'Failed to update notification settings');
    }
  };

  const notificationOptions = [
    {
      key: 'push_enabled',
      icon: 'notifications',
      color: '#00b4d8',
      title: t.pushNotifications,
      description: t.pushNotificationsDesc,
      value: prefs.push_enabled,
    },
    {
      key: 'payment_reminders',
      icon: 'calendar',
      color: '#10b981',
      title: t.paymentReminders,
      description: t.paymentRemindersDesc,
      value: prefs.payment_reminders,
    },
    {
      key: 'deposit_alerts',
      icon: 'arrow-down-circle',
      color: '#f59e0b',
      title: t.depositAlerts,
      description: t.depositAlertsDesc,
      value: prefs.deposit_alerts,
    },
    {
      key: 'monthly_reports',
      icon: 'document-text',
      color: '#8b5cf6',
      title: t.monthlyReports,
      description: t.monthlyReportsDesc,
      value: prefs.monthly_reports,
    },
  ];

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView style={styles.scrollView} contentContainerStyle={styles.scrollContent}>
        {/* Header */}
        <View style={styles.header}>
          <TouchableOpacity onPress={() => router.back()} style={styles.backButton}>
            <Ionicons name="arrow-back" size={24} color="#ffffff" />
          </TouchableOpacity>
          <Text style={styles.headerTitle}>{t.notificationSettings}</Text>
        </View>

        {/* Info Card */}
        <View style={styles.infoCard}>
          <Ionicons name="information-circle" size={24} color="#00b4d8" />
          <Text style={styles.infoText}>
            {language === 'es'
              ? 'Personaliza qu\u00e9 notificaciones recibir\u00e1s de FIDUS'
              : 'Customize which notifications you receive from FIDUS'}
          </Text>
        </View>

        {/* Notification Options */}
        <View style={styles.optionsContainer}>
          {notificationOptions.map((option, index) => (
            <View key={option.key} style={styles.optionItem}>
              <View style={styles.optionLeft}>
                <View style={[styles.optionIcon, { backgroundColor: `${option.color}20` }]}>
                  <Ionicons name={option.icon as any} size={22} color={option.color} />
                </View>
                <View style={styles.optionInfo}>
                  <Text style={styles.optionTitle}>{option.title}</Text>
                  <Text style={styles.optionDescription}>{option.description}</Text>
                </View>
              </View>
              <Switch
                value={option.value}
                onValueChange={(value) => handleToggle(option.key, value)}
                trackColor={{ false: '#2a3444', true: '#00b4d8' }}
                thumbColor="#ffffff"
              />
            </View>
          ))}
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0a0f1a',
  },
  scrollView: {
    flex: 1,
  },
  scrollContent: {
    paddingHorizontal: 16,
    paddingBottom: 24,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 16,
  },
  backButton: {
    marginRight: 16,
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: '700',
    color: '#ffffff',
  },
  infoCard: {
    backgroundColor: 'rgba(0, 180, 216, 0.1)',
    borderRadius: 12,
    padding: 16,
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
    marginBottom: 24,
  },
  infoText: {
    flex: 1,
    fontSize: 14,
    color: '#00b4d8',
    lineHeight: 20,
  },
  optionsContainer: {
    gap: 12,
  },
  optionItem: {
    backgroundColor: '#1a2332',
    borderRadius: 12,
    padding: 16,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  optionLeft: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
    marginRight: 12,
  },
  optionIcon: {
    width: 44,
    height: 44,
    borderRadius: 12,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  optionInfo: {
    flex: 1,
  },
  optionTitle: {
    fontSize: 16,
    fontWeight: '500',
    color: '#ffffff',
  },
  optionDescription: {
    fontSize: 12,
    color: '#6b7280',
    marginTop: 4,
    lineHeight: 16,
  },
});
