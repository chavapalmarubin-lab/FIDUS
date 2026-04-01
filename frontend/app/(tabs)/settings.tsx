import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Alert,
  Linking,
  Switch,
  Platform,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { useRouter } from 'expo-router';
import { useLanguage } from '../../src/context/LanguageContext';
import { useAuth } from '../../src/context/AuthContext';
import { translations } from '../../src/i18n/translations';

export default function SettingsScreen() {
  const router = useRouter();
  const { language, setLanguage } = useLanguage();
  const { user, logout, toggleBiometric, biometricAvailable } = useAuth();
  const t = translations[language];

  const handleLogout = () => {
    Alert.alert(
      t.logout,
      t.logoutConfirm,
      [
        { text: t.cancel, style: 'cancel' },
        {
          text: t.logout,
          style: 'destructive',
          onPress: async () => {
            await logout();
            router.replace('/login');
          },
        },
      ]
    );
  };

  const handleBiometricToggle = async (value: boolean) => {
    const success = await toggleBiometric(value);
    if (!success) {
      Alert.alert(t.error, 'Failed to update biometric settings');
    }
  };

  const handleOpenLucrum = () => {
    Linking.openURL('https://my.lucrumfx.com');
  };

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView style={styles.scrollView} contentContainerStyle={styles.scrollContent}>
        {/* Header */}
        <View style={styles.header}>
          <Text style={styles.headerTitle}>{t.settings}</Text>
        </View>

        {/* Profile Section */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>{t.profile}</Text>
          <TouchableOpacity style={styles.profileCard} onPress={() => router.push('/edit-profile')}>
            <View style={styles.avatarContainer}>
              <Text style={styles.avatarText}>
                {user?.name?.charAt(0).toUpperCase() || 'U'}
              </Text>
            </View>
            <View style={styles.profileInfo}>
              <Text style={styles.profileName}>{user?.name || 'User'}</Text>
              <Text style={styles.profileEmail}>{user?.email || ''}</Text>
            </View>
            <Ionicons name="chevron-forward" size={20} color="#6b7280" />
          </TouchableOpacity>
        </View>

        {/* Language Section */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>{t.language}</Text>
          <View style={styles.languageContainer}>
            <TouchableOpacity
              style={[
                styles.languageButton,
                language === 'en' && styles.languageButtonActive,
              ]}
              onPress={() => setLanguage('en')}
            >
              <Text
                style={[
                  styles.languageText,
                  language === 'en' && styles.languageTextActive,
                ]}
              >
                English
              </Text>
            </TouchableOpacity>
            <TouchableOpacity
              style={[
                styles.languageButton,
                language === 'es' && styles.languageButtonActive,
              ]}
              onPress={() => setLanguage('es')}
            >
              <Text
                style={[
                  styles.languageText,
                  language === 'es' && styles.languageTextActive,
                ]}
              >
                Espa\u00f1ol
              </Text>
            </TouchableOpacity>
          </View>
        </View>

        {/* Security Section */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>{t.security}</Text>
          
          {biometricAvailable && Platform.OS !== 'web' && (
            <View style={styles.settingItem}>
              <View style={styles.settingItemLeft}>
                <View style={[styles.menuIcon, { backgroundColor: 'rgba(0, 180, 216, 0.1)' }]}>
                  <Ionicons name="finger-print" size={20} color="#00b4d8" />
                </View>
                <View style={styles.settingItemInfo}>
                  <Text style={styles.settingItemText}>{t.biometricLogin}</Text>
                  <Text style={styles.settingItemDesc}>{t.biometricDescription}</Text>
                </View>
              </View>
              <Switch
                value={user?.biometricEnabled || false}
                onValueChange={handleBiometricToggle}
                trackColor={{ false: '#2a3444', true: '#00b4d8' }}
                thumbColor="#ffffff"
              />
            </View>
          )}

          <TouchableOpacity style={styles.menuItem} onPress={() => router.push('/change-password')}>
            <View style={styles.menuItemLeft}>
              <View style={[styles.menuIcon, { backgroundColor: 'rgba(239, 68, 68, 0.1)' }]}>
                <Ionicons name="lock-closed-outline" size={20} color="#ef4444" />
              </View>
              <Text style={styles.menuItemText}>{t.changePassword}</Text>
            </View>
            <Ionicons name="chevron-forward" size={20} color="#6b7280" />
          </TouchableOpacity>
        </View>

        {/* Notifications Section */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>{t.notifications}</Text>
          <TouchableOpacity style={styles.menuItem} onPress={() => router.push('/notification-settings')}>
            <View style={styles.menuItemLeft}>
              <View style={[styles.menuIcon, { backgroundColor: 'rgba(16, 185, 129, 0.1)' }]}>
                <Ionicons name="notifications-outline" size={20} color="#10b981" />
              </View>
              <Text style={styles.menuItemText}>{t.notificationSettings}</Text>
            </View>
            <Ionicons name="chevron-forward" size={20} color="#6b7280" />
          </TouchableOpacity>
        </View>

        {/* Actions Section */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>{t.actions}</Text>
          
          <TouchableOpacity style={styles.menuItem} onPress={() => router.push('/transactions')}>
            <View style={styles.menuItemLeft}>
              <View style={[styles.menuIcon, { backgroundColor: 'rgba(139, 92, 246, 0.1)' }]}>
                <Ionicons name="list-outline" size={20} color="#8b5cf6" />
              </View>
              <Text style={styles.menuItemText}>{t.transactionHistory}</Text>
            </View>
            <Ionicons name="chevron-forward" size={20} color="#6b7280" />
          </TouchableOpacity>

          <TouchableOpacity style={styles.menuItem} onPress={() => router.push('/withdraw')}>
            <View style={styles.menuItemLeft}>
              <View style={[styles.menuIcon, { backgroundColor: 'rgba(245, 158, 11, 0.1)' }]}>
                <Ionicons name="wallet-outline" size={20} color="#f59e0b" />
              </View>
              <Text style={styles.menuItemText}>{t.withdrawFunds}</Text>
            </View>
            <Ionicons name="chevron-forward" size={20} color="#6b7280" />
          </TouchableOpacity>

          <TouchableOpacity style={styles.menuItem} onPress={handleOpenLucrum}>
            <View style={styles.menuItemLeft}>
              <View style={[styles.menuIcon, { backgroundColor: 'rgba(0, 180, 216, 0.1)' }]}>
                <Ionicons name="open-outline" size={20} color="#00b4d8" />
              </View>
              <Text style={styles.menuItemText}>{t.goToLucrum}</Text>
            </View>
            <Ionicons name="chevron-forward" size={20} color="#6b7280" />
          </TouchableOpacity>
        </View>

        {/* Logout */}
        <TouchableOpacity style={styles.logoutButton} onPress={handleLogout}>
          <Ionicons name="log-out-outline" size={20} color="#ef4444" />
          <Text style={styles.logoutText}>{t.logout}</Text>
        </TouchableOpacity>

        {/* Version */}
        <Text style={styles.versionText}>FIDUS App v2.0.0</Text>
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
    paddingVertical: 16,
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: '700',
    color: '#ffffff',
  },
  section: {
    marginBottom: 24,
  },
  sectionTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#6b7280',
    marginBottom: 12,
    textTransform: 'uppercase',
    letterSpacing: 1,
  },
  profileCard: {
    backgroundColor: '#1a2332',
    borderRadius: 12,
    padding: 16,
    flexDirection: 'row',
    alignItems: 'center',
  },
  avatarContainer: {
    width: 56,
    height: 56,
    borderRadius: 28,
    backgroundColor: '#00b4d8',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 16,
  },
  avatarText: {
    fontSize: 24,
    fontWeight: '600',
    color: '#ffffff',
  },
  profileInfo: {
    flex: 1,
  },
  profileName: {
    fontSize: 18,
    fontWeight: '600',
    color: '#ffffff',
  },
  profileEmail: {
    fontSize: 14,
    color: '#6b7280',
    marginTop: 4,
  },
  languageContainer: {
    flexDirection: 'row',
    gap: 12,
  },
  languageButton: {
    flex: 1,
    backgroundColor: '#1a2332',
    borderRadius: 12,
    padding: 16,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#2a3444',
  },
  languageButtonActive: {
    borderColor: '#00b4d8',
    backgroundColor: 'rgba(0, 180, 216, 0.1)',
  },
  languageText: {
    fontSize: 16,
    fontWeight: '500',
    color: '#6b7280',
  },
  languageTextActive: {
    color: '#00b4d8',
  },
  settingItem: {
    backgroundColor: '#1a2332',
    borderRadius: 12,
    padding: 16,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: 12,
  },
  settingItemLeft: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  settingItemInfo: {
    flex: 1,
  },
  settingItemText: {
    fontSize: 16,
    color: '#ffffff',
  },
  settingItemDesc: {
    fontSize: 12,
    color: '#6b7280',
    marginTop: 2,
  },
  menuItem: {
    backgroundColor: '#1a2332',
    borderRadius: 12,
    padding: 16,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: 12,
  },
  menuItemLeft: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  menuIcon: {
    width: 40,
    height: 40,
    borderRadius: 10,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  menuItemText: {
    fontSize: 16,
    color: '#ffffff',
  },
  logoutButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 8,
    backgroundColor: 'rgba(239, 68, 68, 0.1)',
    borderRadius: 12,
    padding: 16,
    marginTop: 8,
  },
  logoutText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#ef4444',
  },
  versionText: {
    textAlign: 'center',
    color: '#6b7280',
    fontSize: 12,
    marginTop: 24,
  },
});
