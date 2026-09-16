import { MaterialCommunityIcons } from '@expo/vector-icons';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { LinearGradient } from 'expo-linear-gradient';
import { useState } from 'react';
import { Image, StyleSheet, Text, TextInput, TouchableOpacity, View } from 'react-native';

// Substitua pelo seu IP ou link do Ngrok
const API_URL = "https://froglike-cataleya-quirkily.ngrok-free.dev"; 

export default function LoginScreen({ navigation }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');

  const handleLogin = async () => {
    if (!email || !password) {
      setErrorMsg("Preencha todos os campos");
      return;
    }

    setLoading(true);
    setErrorMsg('');

    try {
      // Comunicação direta com o seu backend Django
      const response = await fetch(`${API_URL}/api/token/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'ngrok-skip-browser-warning': 'true'
        },
        body: JSON.stringify({ username: email, password: password })
      });

      if (response.ok) {
        const data = await response.json();
        await AsyncStorage.setItem('session_token', data.access);
        
        // Redireciona para o app principal após o login com sucesso
        navigation.replace('MainApp');
      } else {
        setErrorMsg("Email ou senha incorretos.");
      }
    } catch (error) {
      setErrorMsg("Erro de conexão com a internet.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <View style={styles.container}>
      {/* O Degradê Nativo Substituindo o GradientRoundedLayout */}
      <LinearGradient
        colors={['#3AC0ED', '#72FC90']}
        style={styles.headerGradient}
      >
        <Image 
          source={require('../../../assets/images/react-logo.png')} // Ajuste o caminho da sua logo
          style={styles.logo} 
        />
        <Text style={styles.title}>VigiAA</Text>
        <Text style={styles.subtitle}>Entre na sua conta</Text>

        <View style={styles.inputContainer}>
          <MaterialCommunityIcons name="email-outline" size={20} color="#777" />
          <TextInput
            style={styles.input}
            placeholder="email@domain.com"
            value={email}
            onChangeText={setEmail}
            keyboardType="email-address"
            autoCapitalize="none"
          />
        </View>

        <View style={styles.inputContainer}>
          <MaterialCommunityIcons name="lock-outline" size={20} color="#777" />
          <TextInput
            style={styles.input}
            placeholder="senha"
            value={password}
            onChangeText={setPassword}
            secureTextEntry
          />
        </View>

        <TouchableOpacity style={styles.loginButton} onPress={handleLogin} disabled={loading}>
          <Text style={styles.loginButtonText}>{loading ? "Conectando..." : "Continue"}</Text>
        </TouchableOpacity>

        {errorMsg ? <Text style={styles.errorText}>{errorMsg}</Text> : null}
      </LinearGradient>

      {/* Parte Inferior */}
      <View style={styles.footer}>
        <TouchableOpacity onPress={() => navigation.navigate('ForgotPassword')}>
          <Text style={styles.forgotPassword}>Esqueci minha senha</Text>
        </TouchableOpacity>

        <View style={styles.dividerContainer}>
          <View style={styles.dividerLine} />
          <Text style={styles.dividerText}>ou</Text>
          <View style={styles.dividerLine} />
        </View>

        <TouchableOpacity style={styles.googleButton}>
          <MaterialCommunityIcons name="google" size={20} color="#DB4437" />
          <Text style={styles.googleButtonText}>Continue com Google</Text>
        </TouchableOpacity>

        <Text style={styles.termsText}>
          Ao clicar em continuar, você aceita nossos{"\n"}
          <Text style={{ fontWeight: 'bold' }}>Termos de Serviço</Text> e <Text style={{ fontWeight: 'bold' }}>Política de Privacidade</Text>
        </Text>

        <View style={styles.registerContainer}>
          <Text style={styles.registerText}>Não possui uma conta? </Text>
          <TouchableOpacity onPress={() => navigation.navigate('Register')}>
            <Text style={styles.registerLink}>Crie sua conta aqui</Text>
          </TouchableOpacity>
        </View>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#FFF' },
  headerGradient: {
    flex: 0.65,
    borderBottomLeftRadius: 60,
    borderBottomRightRadius: 60,
    padding: 30,
    alignItems: 'center',
    justifyContent: 'center',
  },
  logo: { width: 100, height: 100, marginBottom: 10, resizeMode: 'contain' },
  title: { fontSize: 28, fontWeight: 'bold', color: '#000' },
  subtitle: { fontSize: 16, fontWeight: '600', marginBottom: 20 },
  inputContainer: {
    flexDirection: 'row',
    backgroundColor: '#FFF',
    borderRadius: 8,
    height: 50,
    width: '100%',
    alignItems: 'center',
    paddingHorizontal: 15,
    marginBottom: 15,
  },
  input: { flex: 1, marginLeft: 10, color: '#000' },
  loginButton: {
    backgroundColor: '#000',
    width: '100%',
    padding: 15,
    borderRadius: 8,
    alignItems: 'center',
    marginTop: 10,
  },
  loginButtonText: { color: '#FFF', fontWeight: 'bold', fontSize: 16 },
  errorText: { color: 'red', marginTop: 10, fontSize: 12 },
  footer: { flex: 0.35, padding: 30, justifyContent: 'center', backgroundColor: '#FFF' },
  forgotPassword: { color: '#1D76D2', textAlign: 'center', fontWeight: 'bold', marginBottom: 20 },
  dividerContainer: { flexDirection: 'row', alignItems: 'center', marginBottom: 20 },
  dividerLine: { flex: 1, height: 1, backgroundColor: '#E0E0E0' },
  dividerText: { marginHorizontal: 10, color: '#999', fontSize: 12 },
  googleButton: {
    flexDirection: 'row',
    backgroundColor: '#F5F5F5',
    padding: 15,
    borderRadius: 8,
    alignItems: 'center',
    justifyContent: 'center',
    borderWidth: 1,
    borderColor: '#E0E0E0',
    marginBottom: 20,
  },
  googleButtonText: { color: '#000', marginLeft: 10, fontWeight: '500' },
  termsText: { textAlign: 'center', color: '#999', fontSize: 11, marginBottom: 20 },
  registerContainer: { flexDirection: 'row', justifyContent: 'center' },
  registerText: { color: '#999' },
  registerLink: { color: '#1D76D2', fontWeight: 'bold' },
});