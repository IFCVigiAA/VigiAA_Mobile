import { MaterialCommunityIcons } from '@expo/vector-icons';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { LinearGradient } from 'expo-linear-gradient';
import { useState } from 'react';
import { Image, Linking, StyleSheet, Text, TextInput, TouchableOpacity, View } from 'react-native';

// Substitua pelo seu IP ou link do Ngrok
const API_URL = "https://froglike-cataleya-quirkily.ngrok-free.dev"; 

// Função simples para gerar um ID único sem precisar instalar bibliotecas extras
const generateUUID = () => {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
    var r = Math.random() * 16 | 0, v = c === 'x' ? r : (r & 0x3 | 0x8);
    return v.toString(16);
  });
};

export default function LoginScreen({ navigation }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');

  // --- LOGIN TRADICIONAL ---
  const handleLogin = async () => {
    if (!email || !password) {
      setErrorMsg("Preencha todos os campos");
      return;
    }

    setLoading(true);
    setErrorMsg('');

    try {
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

  // --- LOGIN COM GOOGLE (Nova Função) ---
  const handleGoogleLogin = async () => {
    setLoading(true);
    setErrorMsg('Aguardando navegador...');
    
    const loginId = generateUUID();
    const authUrl = `${API_URL}/api/start-login/?login_id=${loginId}`;

    try {
      // 1. Abre o navegador nativo do celular no link do seu backend
      await Linking.openURL(authUrl);

      // 2. Começa a perguntar pro backend a cada 2 segundos se o login deu certo
      let attempts = 0;
      const maxAttempts = 30; // Máximo de 1 minuto esperando (30 tentativas x 2s)

      const checkLoginInterval = setInterval(async () => {
        attempts++;
        
        // Se passar de 1 minuto, desiste e cancela a busca
        if (attempts >= maxAttempts) {
          clearInterval(checkLoginInterval);
          setErrorMsg("Tempo limite esgotado.");
          setLoading(false);
          return;
        }

        try {
          const res = await fetch(`${API_URL}/api/check-login/?login_id=${loginId}`, {
            headers: { 'ngrok-skip-browser-warning': 'true' }
          });
          
          if (res.ok) {
            const data = await res.json();
            
            // Se o backend confirmar que o usuário logou lá no navegador
            if (data.status === 'success' && data.access_token) {
              clearInterval(checkLoginInterval); // Para de perguntar
              await AsyncStorage.setItem('session_token', data.access_token); // Salva o token
              setErrorMsg('Conectado! Redirecionando...');
              
              // Pequeno delay para o usuário ler a mensagem de sucesso antes de pular de tela
              setTimeout(() => {
                navigation.replace('MainApp');
              }, 1000);
            }
          }
        } catch (err) {
          // Erros de rede enquanto testa a API são ignorados para tentar de novo no próximo segundo
        }
      }, 2000);

    } catch (error) {
      setErrorMsg("Erro ao abrir o Google");
      setLoading(false);
    }
  };

  return (
    <View style={styles.container}>
      <LinearGradient
        colors={['#3AC0ED', '#72FC90']}
        style={styles.headerGradient}
      >
        <Image 
          source={require('../../../assets/images/logo-sem-fundo.png')} 
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

        {/* --- O BOTÃO AGORA CHAMA A FUNÇÃO --- */}
        <TouchableOpacity style={styles.googleButton} onPress={handleGoogleLogin} disabled={loading}>
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